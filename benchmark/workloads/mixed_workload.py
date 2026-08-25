from concurrent.futures import ThreadPoolExecutor
import time


def run(driver, node_ids, concurrency=10, operations=100):
    def one(i):
        node_id = node_ids[i % len(node_ids)]
        with driver.session() as session:
            if i % 5 == 0:
                session.run("MERGE (a:Person {id:$id}) SET a.last_benchmark_write=$ts", id=node_id, ts=time.time()).consume()
            else:
                session.run("MATCH (n:Person {id:$id}) RETURN n.id", id=node_id).consume()
    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        list(pool.map(one, range(operations)))
    elapsed = time.perf_counter() - start
    return {"operations": operations, "concurrency": concurrency, "seconds": elapsed,
            "qps": operations / elapsed}
