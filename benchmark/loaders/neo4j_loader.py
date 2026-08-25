import time
from benchmark.utils.connection import bolt_driver
from benchmark.utils.dataset import load_edges


def load(driver, edge_file, batch_size=1000):
    edges = list(load_edges(edge_file))
    start = time.perf_counter()
    with driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n").consume()
        for i in range(0, len(edges), batch_size):
            batch = edges[i:i + batch_size]
            session.run(
                "UNWIND $rows AS r MERGE (a:Person {id:r.source}) MERGE (b:Person {id:r.target}) MERGE (a)-[:KNOWS]->(b)",
                rows=[{"source": s, "target": t} for s, t in batch],
            ).consume()
    elapsed = time.perf_counter() - start
    nodes = len({x for e in edges for x in e})
    return {"edges": len(edges), "nodes": nodes, "seconds": elapsed,
            "nodes_per_sec": nodes / elapsed, "relationships_per_sec": len(edges) / elapsed}
