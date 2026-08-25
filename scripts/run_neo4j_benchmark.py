import json
import time
from pathlib import Path

from benchmark.utils.config import Settings
from benchmark.utils.connection import bolt_driver
from benchmark.utils.dataset import download_pokec, sample_start_nodes
from benchmark.utils.metrics import summarize_ms

from benchmark.workloads.lookup import point_lookup
from benchmark.workloads.traversal import traversal
from benchmark.workloads.aggregation import count_people, group_by_degree
from benchmark.workloads.mixed_workload import run as mixed_run


OUT = (
    Path(__file__).resolve().parents[1]
    / "benchmark"
    / "results"
    / "raw"
)


def measure(session, fn, args, iterations, warmup):
    for _ in range(warmup):
        fn(session, *args)

    values = []

    for _ in range(iterations):
        start = time.perf_counter()
        fn(session, *args)
        values.append((time.perf_counter() - start) * 1000)

    return summarize_ms(values)


def main():
    s = Settings()

    edge_file = download_pokec(s.edge_limit)
    starts = sample_start_nodes(edge_file, 100)

    driver = bolt_driver(
        s.neo4j_uri,
        s.neo4j_username,
        s.neo4j_password,
    )

    rows = []

    try:
        with driver.session(database="neo4j") as session:

            print("Checking Neo4j dataset...")

            nodes = session.run(
                "MATCH (n:Person) RETURN count(n) AS c"
            ).single()["c"]

            relationships = session.run(
                "MATCH ()-[r:KNOWS]->() RETURN count(r) AS c"
            ).single()["c"]

            print(f"Nodes: {nodes:,}")
            print(f"Relationships: {relationships:,}")

            if relationships != s.edge_limit:
                raise RuntimeError(
                    f"Expected {s.edge_limit:,} relationships, "
                    f"found {relationships:,}"
                )

            for hops in (1, 2, 3):
                print(f"Running {hops}-hop traversal...")

                rows.append({
                    "platform": "Neo4j",
                    "metric": f"traversal_{hops}hop",
                    **measure(
                        session,
                        traversal,
                        (starts[0], hops),
                        s.read_iterations,
                        s.warmup_iterations,
                    ),
                })

            print("Running point lookup...")

            rows.append({
                "platform": "Neo4j",
                "metric": "point_lookup",
                **measure(
                    session,
                    point_lookup,
                    (starts[0],),
                    s.read_iterations,
                    s.warmup_iterations,
                ),
            })

            print("Running aggregation count...")

            rows.append({
                "platform": "Neo4j",
                "metric": "aggregation_count",
                **measure(
                    session,
                    lambda x: count_people(x),
                    (),
                    s.read_iterations,
                    s.warmup_iterations,
                ),
            })

            print("Running aggregation group-by...")

            rows.append({
                "platform": "Neo4j",
                "metric": "aggregation_group_by",
                **measure(
                    session,
                    lambda x: group_by_degree(x),
                    (),
                    s.read_iterations,
                    s.warmup_iterations,
                ),
            })

        print("Running mixed workload...")

        rows.append({
            "platform": "Neo4j",
            "metric": "mixed_workload",
            **mixed_run(
                driver,
                starts,
                s.concurrency,
                s.read_iterations,
            ),
        })

    finally:
        driver.close()

    OUT.mkdir(parents=True, exist_ok=True)

    output = OUT / "neo4j_results.json"

    output.write_text(
        json.dumps(rows, indent=2),
        encoding="utf-8",
    )

    print("\nBenchmark complete.")
    print(json.dumps(rows, indent=2))
    print(f"\nResults saved to: {output}")


if __name__ == "__main__":
    main()