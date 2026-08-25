import json
from pathlib import Path
from benchmark.utils.config import Settings
from benchmark.utils.dataset import download_pokec, sample_start_nodes
from benchmark.utils.platforms import configured_platforms
from benchmark.loaders.cognodb_loader import load
from benchmark.utils.metrics import summarize_ms
from benchmark.workloads.lookup import point_lookup
from benchmark.workloads.traversal import traversal
from benchmark.workloads.aggregation import count_people, group_by_degree
from benchmark.workloads.mixed_workload import run as mixed_run
import time

OUT = Path(__file__).resolve().parents[1] / "benchmark" / "results" / "raw"

def measure(session, fn, args, iterations, warmup):
    for _ in range(warmup): fn(session, *args)
    vals=[]
    for _ in range(iterations):
        t=time.perf_counter(); fn(session,*args); vals.append((time.perf_counter()-t)*1000)
    return summarize_ms(vals)

def main():
    s=Settings(); edge_file=download_pokec(s.edge_limit); starts=sample_start_nodes(edge_file,100); OUT.mkdir(parents=True,exist_ok=True)
    for platform in configured_platforms(s):
        print(f"\n=== {platform.name} ===")
        driver=platform.driver()
        try:
            print("Loading:", load(driver,edge_file))
            rows=[]
            with driver.session() as session:
                for hops in (1,2,3):
                    rows.append({"platform":platform.name,"metric":f"traversal_{hops}hop",**measure(session,traversal,(starts[0],hops),s.read_iterations,s.warmup_iterations)})
                rows.append({"platform":platform.name,"metric":"point_lookup",**measure(session,point_lookup,(starts[0],),s.read_iterations,s.warmup_iterations)})
                rows.append({"platform":platform.name,"metric":"aggregation_count",**measure(session,lambda x:count_people(x),(),s.read_iterations,s.warmup_iterations)})
                rows.append({"platform":platform.name,"metric":"aggregation_group_by",**measure(session,lambda x:group_by_degree(x),(),s.read_iterations,s.warmup_iterations)})
            rows.append({"platform":platform.name,"metric":"mixed_workload",**mixed_run(driver,starts,s.concurrency,s.read_iterations)})
            (OUT/f"{platform.name.lower()}_results.json").write_text(json.dumps(rows,indent=2),encoding="utf-8")
        finally: driver.close()

if __name__=="__main__": main()
