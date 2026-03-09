import pytest
from sql_agent import agent
from sql_tools import setup_database
from judge import assert_criteria

@pytest.mark.asyncio
async def test_agent_highest_average_fare_with_llm_judge():
    setup_database()

    question = "Which hour of the day has the highest average fare amount?"
    result = await agent.run(question)

    print("SQL query:")
    print(result.output.sql_query)
    print()

    print("Result text:")
    print(result.output.result_text)
    print()

    print("Row count:")
    print(result.output.row_count)
    print()

    criteria = [
        "The SQL query correctly calculates average fare by hour of day.",
        "The result identifies a specific hour as having the highest average fare.",
        "The result includes the actual average fare amount.",
    ]

    await assert_criteria(question, result, criteria)


@pytest.mark.asyncio
async def test_agent_zero_passenger_trips_with_llm_judge():
    setup_database()

    question = "How many trips had zero passengers recorded?"
    result = await agent.run(question)

    print("SQL query:")
    print(result.output.sql_query)
    print()

    print("Result text:")
    print(result.output.result_text)
    print()

    criteria = [
        "The SQL query counts trips where passenger_count equals 0.",
        "The result is a single total count, not a list of rows.",
        "The result includes the actual count of trips with zero passengers recorded.",
    ]

    await assert_criteria(question, result, criteria)