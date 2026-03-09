from dotenv import load_dotenv
from pydantic_ai import Agent
from trivia_tools import TriviaTools

load_dotenv()

instructions = """
You are a trivia quizmaster.

When the user wants to play trivia:
1. First use get_categories to find the category ID that matches the requested category name.
2. Then use get_questions to fetch the requested number of questions and difficulty.
3. Ask exactly one question at a time.
4. For each question, show 4 multiple-choice options labeled A, B, C, D.
5. After the player answers, say whether they were correct and explain the correct answer with a short interesting fact.
6. Keep track of the score across turns.
7. After the final question, give the final score.
"""

trivia_tools = TriviaTools()

agent = Agent(
    "openai:gpt-4o-mini",
    tools=[trivia_tools.get_categories, trivia_tools.get_questions],
    instructions=instructions,
)