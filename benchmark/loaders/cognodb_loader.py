from benchmark.utils.dataset import load_edges


def load(driver, edge_file, batch_size=250):
    edges = list(load_edges(edge_file))

    total = len(edges)
    loaded = 0

    with driver.session() as session:

        # Create index for fast Person ID lookup
        try:
            session.run(
                "CREATE INDEX person_id_index IF NOT EXISTS "
                "FOR (p:Person) ON (p.id)"
            ).consume()
        except Exception:
            pass

        for start in range(0, total, batch_size):

            batch = edges[start:start + batch_size]

            session.run(
                """
                UNWIND $rows AS r
                MERGE (a:Person {id: r.source})
                MERGE (b:Person {id: r.target})
                MERGE (a)-[:KNOWS]->(b)
                """,
                rows=[
                    {
                        "source": source,
                        "target": target
                    }
                    for source, target in batch
                ]
            ).consume()

            loaded += len(batch)

            print(
                f"Loaded {loaded:,}/{total:,} edges "
                f"({loaded / total * 100:.1f}%)"
            )

    return loaded