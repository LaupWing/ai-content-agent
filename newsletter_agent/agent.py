"""
Newsletter Agent - Multi-agent system for creating high-quality newsletters
with section-by-section research pipeline and Google Search integration

Architecture:
- Root coordinator agent (handles user requests)
- Newsletter creation as SequentialAgent pipeline
- LoopAgent for iterating through sections
"""
from google.adk.agents import Agent, SequentialAgent, LoopAgent
from google.adk.tools import AgentTool
from . import prompt
from .sub_agents.planner.agent import planner
from .sub_agents.researcher.agent import researcher
from .sub_agents.writer.agent import writer
from .sub_agents.formatter.agent import formatter


# ═══════════════════════════════════════════════════════════
# SECTION RESEARCH LOOP
# ═══════════════════════════════════════════════════════════
# This loop will iterate through sections and research each one
# The researcher agent will:
# 1. Check state["sections"] array
# 2. Get the current section index from state["current_section_index"]
# 3. Research that section
# 4. Increment the index
# 5. Stop when all sections are done

section_research_loop = LoopAgent(
    name="section_research_loop",
    sub_agents=[researcher],
    max_iterations=10  # Max 10 sections per newsletter
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
