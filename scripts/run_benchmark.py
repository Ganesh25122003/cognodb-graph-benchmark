import json
import time
from pathlib import Path

from benchmark.utils.config import Settings
from benchmark.utils.connection import bolt_driver
from benchmark.utils.dataset import download_pokec, sample_start_nodes
from benchmark.utils.metrics import summarize_ms
from benchmark.workloads.lookup import point_lookup, indexed_lookup
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

        elapsed = (time.perf_counter() - start) * 1000
        values.append(elapsed)

    return summarize_ms(values)


def main():
    settings = Settings()

    edge_file = download_pokec(settings.edge_limit)
    starts = sample_start_nodes(edge_file, 100)

    driver = bolt_driver(
        settings.cognodb_uri,
        settings.cognodb_username,
        settings.cognodb_password,
    )

    rows = []

    try:
        with driver.session() as session:

            # Traversal workloads
            for hops in (1, 2, 3):
                rows.append(
                    {
                        "platform": "CognoDB",
                        "metric": f"traversal_{hops}hop",
                        **measure(
                            session,
                            traversal,
                            (starts[0], hops),
                            settings.read_iterations,
                            settings.warmup_iterations,
                        ),
                    }
                )

            # Point lookup
            rows.append(
                {
                    "platform": "CognoDB",
                    "metric": "point_lookup",
                    **measure(
                        session,
                        point_lookup,
                        (starts[0],),
                        settings.read_iterations,
                        settings.warmup_iterations,
                    ),
                }
            )

            # Indexed / filtered lookup
            rows.append(
                {
                    "platform": "CognoDB",
                    "metric": "indexed_lookup",
                    **measure(
                        session,
                        indexed_lookup,
                        (starts[0],),
                        settings.read_iterations,
                        settings.warmup_iterations,
                    ),
                }
            )

            # Aggregation
            rows.append(
                {
                    "platform": "CognoDB",
                    "metric": "aggregation_count",
                    **measure(
                        session,
                        lambda x: count_people(x),
                        (),
                        settings.read_iterations,
                        settings.warmup_iterations,
                    ),
                }
            )

            rows.append(
                {
                    "platform": "CognoDB",
                    "metric": "aggregation_group_by",
                    **measure(
                        session,
                        lambda x: group_by_degree(x),
                        (),
                        settings.read_iterations,
                        settings.warmup_iterations,
                    ),
                }
            )

        # Mixed workload
        rows.append(
            {
                "platform": "CognoDB",
                "metric": "mixed_workload",
                **mixed_run(
                    driver,
                    starts,
                    settings.concurrency,
                    settings.read_iterations,
                ),
            }
        )

    finally:
        driver.close()

    OUT.mkdir(parents=True, exist_ok=True)

    output_file = OUT / "cognodb_results.json"

    with output_file.open("w", encoding="utf-8") as file:
        json.dump(rows, file, indent=2)

    print(json.dumps(rows, indent=2))
    print(f"\nResults saved to: {output_file}")


if __name__ == "__main__":
    main()