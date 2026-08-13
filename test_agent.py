from dotenv import load_dotenv
from agents import Agent, Runner

from tools import search_jobs


load_dotenv()


agent = Agent(
    name="Job Research Agent",

    instructions="""
You are an AI job research agent.

Your job is to find and evaluate real employment opportunities.

When the user asks for jobs:

1. Use the search_jobs tool.
2. Never invent a job listing.
3. Use only information returned by the tool.
4. Clearly distinguish missing information from confirmed information.
5. Prioritize jobs that match the user's requirements.
6. Do not claim that a company accepts international applicants unless
   the available job data provides evidence for it.
7. Include the original job URL whenever available.

Present the strongest matches first.
""",

    tools=[search_jobs],
)


result = Runner.run_sync(
    agent,
    """
Find 5 entry-level marketing jobs.

Priorities:
- Remote
- International applicants
- Visa sponsorship if available
- 0-2 years experience

Give me the strongest matches first.
""",
)


print(result.final_output)