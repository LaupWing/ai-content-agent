"""
Blog Content System - Proper ADK Sub-Agent Architecture
"""

from google.adk.agents import Agent
from prompts.modes.quick_mode import PROMPT as QUICK_PROMPT
from prompts.modes.thoughtout_mode import PROMPT as THOUGHTOUT_PROMPT

# ============================================================================
# SUB-AGENTS: Quick and Thoughtout Blog Writers
# ============================================================================

# Quick Blog Writer - Fast, one-shot generation
quick_blog_agent = Agent(
    name="quick_blog_writer",
    model="gemini-2.0-flash-exp",
    description="Fast blog generation - takes topic and immediately creates complete blog",
    instruction=QUICK_PROMPT,
)

# Thoughtout Blog Writer - Interactive, step-by-step
thoughtout_blog_agent = Agent(
    name="thoughtout_blog_writer",
    model="gemini-2.0-flash-exp",
    description="Interactive blog generation - shows headline options, gathers context, refines iteratively",
    instruction=THOUGHTOUT_PROMPT,
)

# ============================================================================
# PARENT AGENT: Blog Orchestrator
# ============================================================================

root_agent = Agent(
    name="blog_orchestrator",
    model="gemini-2.0-flash-exp",
    description="Coordinates blog creation by routing to appropriate blog writer based on mode",
    instruction="""You coordinate blog creation.

# MODE IS ALREADY SET
The mode is stored in state["mode"] - either "quick" or "thoughtout"
You don't need to ask. Just read it and delegate.

# DELEGATION
Read state["mode"] and delegate:

- If mode = "quick" → Transfer to quick_blog_writer
- If mode = "thoughtout" → Transfer to thoughtout_blog_writer

# YOUR JOB
- Read mode from state
- Delegate to correct agent
- Don't write blogs yourself

That's it.
""",
    sub_agents=[quick_blog_agent, thoughtout_blog_agent],
)

# Export root agent for ADK
__all__ = ['root_agent']
