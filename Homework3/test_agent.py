import pytest # install pytest & pytest-asyncio
from pydantic_ai import capture_run_messages
from sql_agent import agent
from sql_tools import SQLTools, setup_database
from utils import collect_tools

# Agent testing: uv run pytest -s -v (in Powershell)
# test_agent_counts_trips_with_more_than_5_passengers() checks that the agent produces a non-empty SQL query and returns a result containing the correct count from the database, so it is mainly an integration-style correctness test.
# test_agent_calls_schema_before_sql() checks that the agent follows the expected tool-use process by calling get_schema first and run_sql afterward, so it is mainly a workflow test.

@pytest.mark.asyncio
async def test_agent_counts_trips_with_more_than_5_passengers():
    # Make sure the database and trips table exist
    setup_database()

    # Compute the true answer directly from DuckDB
    tools = SQLTools()
    expected_count = tools.con.execute(
        "SELECT COUNT(*) FROM trips WHERE passenger_count > 5"
    ).fetchone()[0]

    # Ask the agent
    result = await agent.run("How many trips had more than 5 passengers?")
    output = result.output

    # Assert the agent produced a SQL query
    assert isinstance(output.sql_query, str)
    assert output.sql_query.strip() != ""

    # Assert the returned text contains the real count
    assert str(expected_count) in output.result_text


@pytest.mark.asyncio
async def test_agent_calls_schema_before_sql():
    setup_database()

    with capture_run_messages() as messages:
        await agent.run("What is the most common payment type?")

    tool_calls = collect_tools(messages)
    print("Tool call order:", tool_calls)

    assert len(tool_calls) > 0 # make sure at least one tool was called
    assert tool_calls[0] == "get_schema" # verify the first tool call was schema inspection
    assert "run_sql" in tool_calls # verify that SQL execution happened