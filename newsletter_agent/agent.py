"""
Newsletter Agent - Multi-agent system for creating high-quality newsletters
with section-by-section research pipeline and Google Search integration

Architecture:
- Root coordinator agent (handles user requests)
- Newsletter creation as SequentialAgent pipeline
- Custom programmatic loop for iterating through sections
"""
from google.adk.agents import Agent, SequentialAgent
from google.adk.tools import AgentTool
from . import prompt
from .sub_agents.planner.agent import planner
from .sub_agents.researcher.agent import researcher
from .sub_agents.writer.agent import writer
from .sub_agents.formatter.agent import formatter
from .section_loop_handler import SectionLoopAgent


# ═══════════════════════════════════════════════════════════
# SECTION RESEARCH LOOP (CUSTOM PROGRAMMATIC AGENT)
# ═══════════════════════════════════════════════════════════
# This is a custom agent that programmatically loops through sections
# Much more reliable than instruction-based iteration!
#
# How it works:
# 1. Reads state["sections"] array (from planner)
# 2. For each section in the array:
#    - Calls researcher sub-agent with that section
#    - Collects the research result
# 3. Stores all results in state["researched_sections"]

section_research_loop = SectionLoopAgent(
    name="section_research_loop",
    researcher_agent=researcher
)


# ═══════════════════════════════════════════════════════════
# NEWSLETTER CREATION PIPELINE (SEQUENTIAL)
# ═══════════════════════════════════════════════════════════
# Sequential pipeline: Planner → Research Loop → Writer → Formatter

newsletter_creation_pipeline = SequentialAgent(
    name="newsletter_creation",
    sub_agents=[
        planner,                # 1. Creates table of contents → state["sections"]
        section_research_loop,  # 2. Loops: researches each section → state["researched_sections"]
        writer,                 # 3. Combines researched sections → complete story
        formatter               # 4. Final formatting
    ]
)


# ═══════════════════════════════════════════════════════════
# ROOT COORDINATOR AGENT
# ═══════════════════════════════════════════════════════════
# This is the main agent that receives user requests
# It routes to the newsletter creation pipeline

newsletter_coordinator = Agent(
    name="newsletter_coordinator",
    model="gemini-2.5-flash",
    instruction=prompt.NEWSLETTER_COORDINATOR_PROMPT,
    description="Main coordinator that handles user requests and routes to newsletter creation pipeline",
    tools=[
        AgentTool(agent=newsletter_creation_pipeline)
    ]
)


# ═══════════════════════════════════════════════════════════
# EXPORT ROOT AGENT (ADK discovers this automatically)
# ═══════════════════════════════════════════════════════════

# The root agent is the coordinator (NOT the sequential pipeline)
# Users interact with this agent
root_agent = newsletter_coordinator
