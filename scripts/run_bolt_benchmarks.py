import json
import time
from pathlib import Path

from benchmark.utils.config import Settings
from benchmark.utils.dataset import download_pokec, sample_start_nodes
from benchmark.utils.platforms import configured_platforms
from benchmark.loaders.neo4j_loader import load
from benchmark.utils.metrics import summarize_ms
from benchmark.workloads.lookup import point_lookup, indexed_lookup
from benchmark.workloads.traversal import traversal
from benchmark.workloads.aggregation import count_people, group_by_degree
from benchmark.workloads.mixed_workload import run as mixed_run


OUT = Path(__file__).resolve().parents[1] / "benchmark" / "results" / "raw"


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

    OUT.mkdir(parents=True, exist_ok=True)

    for platform in configured_platforms(s):
        print(f"\n=== {platform.name} ===")

        driver = platform.driver()

        try:
            print("Loading dataset...")
            load_result = load(driver, edge_file)

            print("Load result:")
            print(json.dumps(load_result, indent=2))

            rows = []

            with driver.session(database="neo4j") as session:

                for hops in (1, 2, 3):
                    rows.append({
                        "platform": platform.name,
                        "metric": f"traversal_{hops}hop",
                        **measure(
                            session,
                            traversal,
                            (starts[0], hops),
                            s.read_iterations,
                            s.warmup_iterations,
                        ),
                    })

                rows.append({
                    "platform": platform.name,
                    "metric": "point_lookup",
                    **measure(
                        session,
                        point_lookup,
                        (starts[0],),
                        s.read_iterations,
                        s.warmup_iterations,
                    ),
                })

                rows.append({
                    "platform": platform.name,
                    "metric": "indexed_lookup",
                    **measure(
                        session,
                        indexed_lookup,
                        (starts[0],),
                        s.read_iterations,
                        s.warmup_iterations,
                    ),
                })

                rows.append({
                    "platform": platform.name,
                    "metric": "aggregation_count",
                    **measure(
                        session,
                        count_people,
                        (),
                        s.read_iterations,
                        s.warmup_iterations,
                    ),
                })

                rows.append({
                    "platform": platform.name,
                    "metric": "aggregation_group_by",
                    **measure(
                        session,
                        group_by_degree,
                        (),
                        s.read_iterations,
                        s.warmup_iterations,
                    ),
                })

            rows.append({
                "platform": platform.name,
                "metric": "mixed_workload",
                **mixed_run(
                    driver,
                    starts,
                    s.concurrency,
                    s.read_iterations,
                ),
            })

            result_file = OUT / f"{platform.name.lower()}_results.json"

            result_file.write_text(
                json.dumps(rows, indent=2),
                encoding="utf-8",
            )

            print(f"Results saved to: {result_file}")

        finally:
            driver.close()


if __name__ == "__main__":
    main()