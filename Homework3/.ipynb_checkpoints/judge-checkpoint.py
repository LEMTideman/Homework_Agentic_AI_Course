# from https://github.com/alexeygrigorev/ai-engineering-buildcamp-code/blob/ff4aff714de350b5d6c931b7b0b00ff122da5814/documentation-agent/tests/judge.py#L69
from pydantic import BaseModel, Field
from pydantic_ai import Agent 
from utils import collect_tools

judge_instructions = """
You are an expert judge evaluating the performance of a SQL agent.

Evaluate the agent only using the evidence provided. Be strict and do not guess.

For each criterion:
- mark passed=true only if the evidence clearly satisfies it
- mark passed=false if the evidence is missing, unclear, or incorrect
- explain your judgement briefly and point to the relevant evidence
""".strip()

class JudgeCriterion(BaseModel):
    """
    Evaluation of a single test requirement or behavioral rule.
    """
    criterion_description: str = Field(
        description="The requirement or rule being evaluated."
    )
    passed: bool = Field(
        description="Whether the requirement was satisfied."
    )
    judgement: str = Field(
        description="Short explanation of why the criterion passed or failed."
    )


class JudgeFeedback(BaseModel):
    """
    The complete evaluation report from the judge agent, summarizing performance across all criteria.
    """
    criteria: list[JudgeCriterion] = Field(
        description="Evaluation results for each criterion."
    )
    feedback: str = Field(
        description="Overall summary of the agent's performance."
    )


# The judge is not an agent because it has no tools
# It is simply a call to the OpenAI API
def create_judge_agent():
    agent = Agent(
        name="judge",
        model="openai:gpt-4o-mini",
        instructions=judge_instructions,
        output_type=JudgeFeedback
    )
    return agent

# Instructions (system prompt) for the judge LLM
judge_user_prompt_template = """
You are evaluating the performance of a SQL agent.
Use only the evidence provided below. Be strict and do not guess.
For each criterion:
- mark passed=true only if the evidence clearly satisfies it
- mark passed=false if the evidence is missing, unclear, or incorrect
- explain your judgement briefly and refer to the evidence

Question:
<QUESTION>
{question}
</QUESTION>

Criteria:
<CRITERIA>
{criteria}
</CRITERIA>

Agent output:
<AGENT_OUTPUT>
{output}
</AGENT_OUTPUT>

Tool calls:
<TOOL_CALLS>
{tool_calls}
</TOOL_CALLS>
""".strip()


async def evaluate_agent_performance(question: str, result, criteria: list[str]) -> JudgeFeedback:
    messages = result.new_messages()
    tool_calls = collect_tools(messages)

    output = result.output
    if hasattr(output, "model_dump_json"):
        output_text = output.model_dump_json(indent=2)
    else:
        output_text = str(output)

    judge_prompt = judge_user_prompt_template.format(
        question=question,
        criteria="\n".join(f"- {c}" for c in criteria),
        output=output_text,
        tool_calls="\n".join(tool_calls) if tool_calls else "(none)",
    )

    judge_agent = create_judge_agent()
    judge_result = await judge_agent.run(judge_prompt)
    return judge_result.output


async def assert_criteria(question: str, result, criteria: list[str]) -> None:
    feedback = await evaluate_agent_performance(question, result, criteria)

    print("Judge feedback:")
    print(feedback.feedback)

    for criterion in feedback.criteria:
        print(f"- {criterion.criterion_description}")
        print(f"  passed: {criterion.passed}")
        print(f"  judgement: {criterion.judgement}")
        assert criterion.passed, f"{criterion.criterion_description}: {criterion.judgement}"