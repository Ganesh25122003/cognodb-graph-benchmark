# CognoDB Graph Database Cloud Benchmark

Benchmark CognoDB Cloud against at least four other graph databases using the same public dataset and logically equivalent workloads.

## Assignment requirements covered
- Public dataset with at least 100,000 relationships.
- Identical dataset across platforms.
- Ingestion throughput: nodes/sec, relationships/sec and wall-clock load time.
- 1-hop, 2-hop and 3-hop traversal p50/p95 latency.
- Point and indexed/filtered lookup p50/p95 latency.
- Aggregation p50/p95 latency.
- Mixed read/write throughput with stated concurrency.
- Observable footprint/specs, otherwise `not observable`.
- Warm-up before reads, repeated measurements and percentile reporting.
- Automated scripts and raw result artifacts.

## Dataset
The harness downloads a reproducible sample from the SNAP soc-Pokec social network and limits it to `EDGE_LIMIT` relationships. The exact generated node/edge counts are written to `benchmark/data/processed/dataset_meta.txt`.

## Platforms
The repository is structured for CognoDB plus four additional graph databases. Before final submission, record the exact platform, tier, vCPU, RAM, storage, region, indexes and connection method in the README and result files. Never fabricate benchmark numbers.

## Setup
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```
Fill credentials in `.env`. Never commit `.env`.

## First run
```powershell
python -m scripts.load_all
python -m scripts.run_benchmark
```

## Important
The benchmark results must be produced by real runs. Do not manually invent or alter performance numbers. The assignment explicitly asks for honest caveats, warm-up, repeated measurements, the same dataset/workloads, and equivalent resources.
