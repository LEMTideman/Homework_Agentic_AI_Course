from dotenv import load_dotenv
from pydantic import BaseModel
from pydantic_ai import Agent
from trivia_tools import TriviaTools

load_dotenv() # necessary for accessing OpenAI key

instructions = """You are a trivia quizmaster. When asked to play trivia:
1. Use the available tools to fetch trivia questions
2. Ask the player one question at a time with multiple choice options
3. Wait for their answer before moving to the next question
4. When the player answers, explain why the correct answer is correct - add interesting context and facts
5. After all questions, give the final score
"""

trivia_tools = TriviaTools()

agent = Agent(
    'openai:gpt-4o-mini',
    tools=[trivia_tools.get_categories, trivia_tools.get_questions],
    instructions=instructions,
)