import time
from benchmark.utils.dataset import load_edges


def load(driver, edge_file, batch_size=5000):
    edges = list(load_edges(edge_file))

    start = time.perf_counter()

    nodes = sorted({node for edge in edges for node in edge})

    with driver.session(database="neo4j") as session:

        # Clean previous benchmark data
        session.run(
            "MATCH (n:Person) DETACH DELETE n"
        ).consume()

        # Ensure fast node lookup
        session.run(
            """
            CREATE CONSTRAINT person_id_unique IF NOT EXISTS
            FOR (n:Person)
            REQUIRE n.id IS UNIQUE
            """
        ).consume()

        # Load nodes
        for i in range(0, len(nodes), batch_size):
            batch = nodes[i:i + batch_size]

            session.run(
                """
                UNWIND $ids AS id
                MERGE (:Person {id: id})
                """,
                ids=batch,
            ).consume()

            print(
                f"Nodes: {min(i + batch_size, len(nodes)):,}/{len(nodes):,}"
            )

        # Load relationships
        for i in range(0, len(edges), batch_size):
            batch = edges[i:i + batch_size]

            session.run(
                """
                UNWIND $rows AS r
                MATCH (a:Person {id: r.source})
                MATCH (b:Person {id: r.target})
                CREATE (a)-[:KNOWS]->(b)
                """,
                rows=[
                    {"source": source, "target": target}
                    for source, target in batch
                ],
            ).consume()

            print(
                f"Relationships: "
                f"{min(i + batch_size, len(edges)):,}/{len(edges):,}"
            )

    elapsed = time.perf_counter() - start

    return {
        "edges": len(edges),
        "nodes": len(nodes),
        "seconds": elapsed,
        "nodes_per_sec": len(nodes) / elapsed,
        "relationships_per_sec": len(edges) / elapsed,
    }