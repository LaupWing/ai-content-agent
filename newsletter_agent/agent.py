"""
Newsletter Agent - Multi-agent system for creating high-quality newsletters
with section-by-section research pipeline and Google Search integration

Architecture:
- SequentialAgent orchestrates the pipeline
- LoopAgent iterates over sections for research
- Uses ADK's native workflow agents
"""
from google.adk.agents import Agent, SequentialAgent, LoopAgent
from . import prompt
from .sub_agents.planner.agent import planner
from .sub_agents.researcher.agent import researcher
from .sub_agents.writer.agent import writer
from .sub_agents.formatter.agent import formatter


# ═══════════════════════════════════════════════════════════
# SECTION RESEARCH LOOP
# ═══════════════════════════════════════════════════════════
# This loop will iterate over sections and research each one

section_research_loop = LoopAgent(
    name="section_research_loop",
    sub_agents=[researcher],
    max_iterations=10  # Max 10 sections per newsletter
)


# ═══════════════════════════════════════════════════════════
# NEWSLETTER PIPELINE (SEQUENTIAL)
# ═══════════════════════════════════════════════════════════
# Sequential pipeline: Planner → Research Loop → Writer → Formatter

newsletter_pipeline = SequentialAgent(
    name="newsletter_pipeline",
    sub_agents=[
        planner,              # 1. Creates table of contents (sections array)
        section_research_loop,  # 2. Loops through sections, researches each
        writer,               # 3. Combines researched sections into story
        formatter             # 4. Final formatting
    ]
)


# ═══════════════════════════════════════════════════════════
# EXPORT ROOT AGENT (ADK discovers this automatically)
# ═══════════════════════════════════════════════════════════

# Export the sequential pipeline as the root agent
root_agent = newsletter_pipeline
