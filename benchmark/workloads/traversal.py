def traversal(session, node_id, hops):
    query = f"MATCH (n:Person {{id:$id}})-[:KNOWS*1..{hops}]->(m) RETURN count(DISTINCT m) AS count"
    return session.run(query, id=node_id).single()["count"]
