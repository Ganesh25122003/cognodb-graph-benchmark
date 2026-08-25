from dataclasses import dataclass
import os
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:
    edge_limit: int = int(os.getenv("EDGE_LIMIT", "200000"))
    warmup_iterations: int = int(os.getenv("WARMUP_ITERATIONS", "10"))
    read_iterations: int = int(os.getenv("READ_ITERATIONS", "100"))
    concurrency: int = int(os.getenv("CONCURRENCY", "10"))

    cognodb_uri: str = os.getenv("COGNODB_URI", "")
    cognodb_username: str = os.getenv("COGNODB_USERNAME", "cognodb")
    cognodb_password: str = os.getenv("COGNODB_PASSWORD", "")

    neo4j_uri: str = os.getenv("NEO4J_URI", "")
    neo4j_username: str = os.getenv("NEO4J_USERNAME", "neo4j")
    neo4j_password: str = os.getenv("NEO4J_PASSWORD", "")

    memgraph_uri: str = os.getenv("MEMGRAPH_URI", "")
    memgraph_username: str = os.getenv("MEMGRAPH_USERNAME", "")
    memgraph_password: str = os.getenv("MEMGRAPH_PASSWORD", "")

    falkordb_uri: str = os.getenv("FALKORDB_URI", "")
    falkordb_username: str = os.getenv("FALKORDB_USERNAME", "")
    falkordb_password: str = os.getenv("FALKORDB_PASSWORD", "")

    arango_url: str = os.getenv("ARANGO_URL", "")
    arango_username: str = os.getenv("ARANGO_USERNAME", "root")
    arango_password: str = os.getenv("ARANGO_PASSWORD", "")
    arango_database: str = os.getenv("ARANGO_DATABASE", "benchmark")
