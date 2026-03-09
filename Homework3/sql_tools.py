import os
import urllib.request
from pydantic import BaseModel
import duckdb

DATA_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-01.parquet"
PARQUET_FILE = "yellow_tripdata_2024-01.parquet"

con = duckdb.connect("taxi.db")

class RunSQLResult(BaseModel):
    """Structured result returned by run_sql()."""
    
    result_text: str
    row_count: int

class SQLTools:
    """Small helper for reading schema information and running SQL on taxi.db.

    This class opens a DuckDB connection and exposes two methods for the agent:
    - get_schema(): returns the schema of the trips table as text
    - run_sql(query): executes a SQL query and returns the results as text

    It is intentionally simple so it can be used directly from Pydantic AI tools.
    """

    def __init__(self, db_path: str = "taxi.db"):
        """Create a connection to the DuckDB database file."""
        self.con = duckdb.connect(db_path)

    def get_schema(self) -> str:
        """Return all columns in the trips table with their DuckDB types."""
        rows = self.con.execute("DESCRIBE trips").fetchall()
        return "\n".join(f"{name} ({dtype})" for name, dtype, *_ in rows)

    def run_sql(self, query: str) -> RunSQLResult:
        """Run a SQL query and return formatted text plus row count."""
        result = self.con.execute(query)

        if result.description is None:
            return RunSQLResult(
                result_text="Query executed successfully.",
                row_count=0,
            )

        headers = [col[0] for col in result.description]
        rows = result.fetchmany(50)

        lines = ["\t".join(headers)]
        lines.extend("\t".join(map(str, row)) for row in rows)

        return RunSQLResult(
            result_text="\n".join(lines),
            row_count=len(rows),
        )

#    def run_sql(self, query: str) -> str:
#        """Run a SQL query and return column headers plus up to 50 rows as text."""
#        result = self.con.execute(query)
#
#        if result.description is None:
#            return "Query executed successfully."
#
#        headers = [col[0] for col in result.description]
#        rows = result.fetchmany(50)
#
#        lines = ["\t".join(headers)]
#        lines.extend("\t".join(map(str, row)) for row in rows)
#        return "\n".join(lines)


def setup_database():
    """Download the parquet file and load it into DuckDB."""
    if not os.path.exists(PARQUET_FILE):
        print(f"Downloading {DATA_URL}...")
        urllib.request.urlretrieve(DATA_URL, PARQUET_FILE)

    con.execute(f"""
        CREATE TABLE IF NOT EXISTS trips AS
        SELECT * FROM '{PARQUET_FILE}'
    """)
    count = con.execute("SELECT COUNT(*) FROM trips").fetchone()[0]
    print(f"Loaded {count} rows")
    return count