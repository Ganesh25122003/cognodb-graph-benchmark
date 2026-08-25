from neo4j import GraphDatabase
from .config import Settings


def bolt_driver(uri: str, username: str, password: str):
    if not uri or not password:
        raise ValueError("Database URI/password is missing. Configure the corresponding .env variables.")
    return GraphDatabase.driver(uri, auth=(username, password))


def verify_bolt(driver, database="neo4j"):
    with driver.session(database=database) as session:
        return session.run("RETURN 1 AS ok").single()["ok"] == 1
