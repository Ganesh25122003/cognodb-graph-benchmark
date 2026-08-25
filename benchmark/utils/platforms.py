from dataclasses import dataclass
from benchmark.utils.config import Settings
from benchmark.utils.connection import bolt_driver

@dataclass(frozen=True)
class BoltPlatform:
    name: str
    uri: str
    username: str
    password: str

    def driver(self):
        return bolt_driver(self.uri, self.username, self.password)


def configured_platforms(s: Settings):
    candidates = [
        BoltPlatform("CognoDB", s.cognodb_uri, s.cognodb_username, s.cognodb_password),
        BoltPlatform("Neo4j", s.neo4j_uri, s.neo4j_username, s.neo4j_password),
        BoltPlatform("Memgraph", s.memgraph_uri, s.memgraph_username, s.memgraph_password),
        BoltPlatform("FalkorDB", s.falkordb_uri, s.falkordb_username, s.falkordb_password),
    ]
    return [p for p in candidates if p.uri and p.password]
