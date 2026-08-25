from pathlib import Path
required = [
'benchmark/data/raw','benchmark/data/processed','benchmark/loaders/cognodb_loader.py','benchmark/loaders/neo4j_loader.py',
'benchmark/results/raw','benchmark/results/processed','benchmark/results/charts','benchmark/utils/config.py','benchmark/utils/connection.py',
'benchmark/utils/dataset.py','benchmark/utils/metrics.py','benchmark/workloads/aggregation.py','benchmark/workloads/lookup.py',
'benchmark/workloads/mixed_workload.py','benchmark/workloads/traversal.py','scripts/load_all.py','scripts/run_benchmark.py',
'.env.example','.gitignore','README.md','requirements.txt']
root=Path(__file__).resolve().parents[1]
missing=[x for x in required if not (root/x).exists()]
print('Missing:' if missing else 'Project structure OK')
for x in missing: print(' -',x)
