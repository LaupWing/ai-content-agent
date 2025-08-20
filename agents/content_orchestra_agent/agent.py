# agent.py
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from agents.thread_expander import thread_expander_agent
from agents.newsletter_generator import newsletter_generator_agent
from agents.reel_script import reel_script_agent
from config import MODEL_GPT_4O

root_agent = Agent(
    name="ContentOrchestrator",
    model=LiteLlm(model=MODEL_GPT_4O),
    description="Orchestrates content creation tasks: threads, newsletters, reels.",
    instruction="""
        You are the root agent. On user request or new content idea, delegate:
        - Use thread_expander_agent for tweet threads.
        - Use newsletter_generator_agent for newsletters.
        - Use reel_script_agent for Instagram reel scripts.
        Coordinate task routing based on content intent.
    """,
    sub_agents=[thread_expander_agent, newsletter_generator_agent, reel_script_agent]
)

print(f"✨ Created root agent {root_agent.name} with sub-agents {[sa.name for sa in root_agent.sub_agents]}")
