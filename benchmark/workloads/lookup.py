def point_lookup(session, node_id):
    return session.run(
        "MATCH (n:Person {id:$id}) RETURN n.id AS id",
        id=node_id
    ).single()


def indexed_lookup(session, node_id):
    return session.run(
        """
        MATCH (n:Person)
        WHERE n.id = $id
        RETURN n.id AS id
        """,
        id=node_id
    ).single()