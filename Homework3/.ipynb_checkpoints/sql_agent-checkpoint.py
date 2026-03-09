from dotenv import load_dotenv
from pydantic import BaseModel
from pydantic_ai import Agent

from sql_tools import SQLTools
load_dotenv() # necessary for accessing OpenAI key

# Import tools: get_schema() is for inspecting the table, and run_sql() is for querying it.
sql_tools = SQLTools()

# Define the output schema (deterministic output formatting with a given set of fields).
# Structured outputs (like tools) use Pydantic to build the JSON schema used for the tool, 
# and to validate the data returned by the model. Structured outputs facilitate debugging. 
class SQLResult(BaseModel):
    sql_query: str
    result_text: str
    row_count: int

# System prompt adapted from LangChain docs (https://docs.langchain.com/oss/python/langchain/sql-agent).
SYSTEM_PROMPT = """
You are an agent designed to interact with a SQL database.

You have access to two tools:
- get_schema(): returns the schema of the trips table
- run_sql(query): executes a SQL query and returns the results as text

When the user asks a question:
1. First call get_schema()
2. Write a correct DuckDB SQL query for the trips table
3. Run it with run_sql(query)
4. Return the final answer as a SQLResult object

Rules:
- Always query only the columns you need
- Unless the user asks for more, limit results to 5 rows
- Do not make any DML statements (INSERT, UPDATE, DELETE, DROP, etc.)
- If a query fails, fix it and try again
- Fill SQLResult like this:
  - sql_query: the SQL query you executed
  - result_text: the exact text returned by run_sql
  - row_count: the number of data rows shown in result_text, excluding the header row
"""

agent = Agent(
    "openai:gpt-4o-mini",
    output_type=SQLResult,
    system_prompt=SYSTEM_PROMPT,
    tools=[sql_tools.get_schema, sql_tools.run_sql],
)