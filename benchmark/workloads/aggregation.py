def count_people(session):
    return session.run("MATCH (n:Person) RETURN count(n) AS count").single()["count"]


def group_by_degree(session):
    return session.run("MATCH (n:Person)-[:KNOWS]->(m:Person) RETURN n.id AS id, count(m) AS degree ORDER BY degree DESC LIMIT 20").data()
