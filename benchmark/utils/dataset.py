from pathlib import Path
import gzip
import random
import requests
import time

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"

URL = "https://snap.stanford.edu/data/soc-pokec-relationships.txt.gz"


def download_pokec(edge_limit=200_000):
    RAW.mkdir(parents=True, exist_ok=True)
    PROCESSED.mkdir(parents=True, exist_ok=True)

    gz_path = RAW / "soc-pokec-relationships.txt.gz"
    edge_path = PROCESSED / "edges.csv"

    # Download dataset if it is not already present
    if not gz_path.exists():
        print("Downloading Pokec dataset...")
        print("This may take a few minutes.")

        for attempt in range(3):
            try:
                with requests.get(
                    URL,
                    stream=True,
                    timeout=(30, 300),
                ) as response:

                    response.raise_for_status()

                    total = int(response.headers.get("content-length", 0))
                    downloaded = 0

                    with gz_path.open("wb") as file:
                        for chunk in response.iter_content(chunk_size=1024 * 1024):
                            if not chunk:
                                continue

                            file.write(chunk)
                            downloaded += len(chunk)

                            if total:
                                percent = downloaded * 100 / total
                                print(
                                    f"\rDownloaded: {percent:.1f}%",
                                    end="",
                                    flush=True,
                                )
                            else:
                                print(
                                    f"\rDownloaded: {downloaded / 1024 / 1024:.1f} MB",
                                    end="",
                                    flush=True,
                                )

                print("\nDownload completed.")
                break

            except Exception as e:
                print(f"\nDownload attempt {attempt + 1} failed: {e}")

                if gz_path.exists():
                    gz_path.unlink()

                if attempt < 2:
                    print("Retrying in 5 seconds...")
                    time.sleep(5)
                else:
                    raise RuntimeError(
                        "Could not download the Pokec dataset."
                    ) from e

    else:
        print("Pokec dataset already downloaded.")

    # Convert the required number of edges to CSV
    if edge_path.exists():
        print(f"Processed dataset already exists: {edge_path}")
        return edge_path

    print(f"Processing first {edge_limit:,} edges...")

    count = 0
    nodes = set()

    with gzip.open(gz_path, "rt", encoding="utf-8") as src, \
            edge_path.open("w", encoding="utf-8") as out:

        out.write("source,target\n")

        for line in src:
            if line.startswith("#") or not line.strip():
                continue

            parts = line.split()

            if len(parts) < 2:
                continue

            source, target = parts[:2]

            out.write(f"{source},{target}\n")

            nodes.add(source)
            nodes.add(target)

            count += 1

            if count >= edge_limit:
                break

    metadata = (
        f"source={URL}\n"
        f"edges={count}\n"
        f"nodes={len(nodes)}\n"
    )

    (PROCESSED / "dataset_meta.txt").write_text(
        metadata,
        encoding="utf-8",
    )

    print(f"Processing completed.")
    print(f"Edges: {count:,}")
    print(f"Nodes: {len(nodes):,}")

    return edge_path


def load_edges(path):
    with open(path, encoding="utf-8") as file:
        next(file)

        for line in file:
            source, target = line.strip().split(",")
            yield source, target


def sample_start_nodes(path, n=100, seed=42):
    nodes = set()

    for source, target in load_edges(path):
        nodes.add(source)
        nodes.add(target)

    rng = random.Random(seed)

    return rng.sample(
        sorted(nodes),
        min(n, len(nodes)),
    )