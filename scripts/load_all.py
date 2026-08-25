import time
from pathlib import Path

from benchmark.utils.config import Settings
from benchmark.utils.dataset import download_pokec
from benchmark.utils.connection import bolt_driver, verify_bolt
from benchmark.loaders.cognodb_loader import load


def main():
    settings = Settings()

    edge_file = download_pokec(200_000)

    driver = bolt_driver(
        settings.cognodb_uri,
        settings.cognodb_username,
        settings.cognodb_password,
    )

    try:
        print("Connection:", verify_bolt(driver))

        print("Loading CognoDB...")
        start = time.perf_counter()

        loaded = load(driver, edge_file)

        elapsed = time.perf_counter() - start

        metadata_file = (
            Path(edge_file).parent / "dataset_meta.txt"
        )

        nodes = "not available"

        if metadata_file.exists():
            for line in metadata_file.read_text(
                encoding="utf-8"
            ).splitlines():
                if line.startswith("nodes="):
                    nodes = int(line.split("=", 1)[1])

        relationships_per_second = (
            loaded / elapsed if elapsed > 0 else 0
        )

        nodes_per_second = (
            nodes / elapsed
            if isinstance(nodes, int) and elapsed > 0
            else 0
        )

        print("\n=== CognoDB Load Results ===")
        print(f"Nodes: {nodes}")
        print(f"Relationships: {loaded}")
        print(f"Load time: {elapsed:.3f} seconds")
        print(f"Nodes/sec: {nodes_per_second:.2f}")
        print(
            f"Relationships/sec: "
            f"{relationships_per_second:.2f}"
        )

    finally:
        driver.close()


if __name__ == "__main__":
    main()