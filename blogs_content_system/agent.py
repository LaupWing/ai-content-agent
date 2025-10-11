"""
Blog Content System - Root Orchestrator
Uses ADK Web UI for testing
"""

from google.adk.agents import Agent
from prompts.modes.quick_mode import PROMPT as QUICK_PROMPT
from prompts.modes.thoughtout_mode import PROMPT as THOUGHTOUT_PROMPT

# Blog Writer Agent - Handles both modes
blog_writer = Agent(
    name="blog_writer",
    model="gemini-2.0-flash-exp",
    instruction="""You are an elite blog writer.

# MODE HANDLING

You receive context about which mode to use. Check the conversation for:
- "quick mode" or user said "quick" → Use quick mode approach
- "thoughtout mode" or user said "thoughtout" → Use thoughtout mode approach

## QUICK MODE
{quick_prompt}

## THOUGHTOUT MODE
{thoughtout_prompt}

When in doubt, ask: "Quick mode (fast) or Thoughtout mode (interactive)?"
""".format(quick_prompt=QUICK_PROMPT, thoughtout_prompt=THOUGHTOUT_PROMPT),
)

# Root Orchestrator Agent
root_agent = Agent(
    name="blog_orchestrator",
    model="gemini-2.0-flash-exp",
    description="Coordinates blog creation and editing",
    instruction="""You are the Blog Content System coordinator.

# SESSION FLOW

1. FIRST INTERACTION
   When user arrives, ask:
   "Quick mode (fast) or Thoughtout mode (step-by-step)?"

   Store their choice in context.

2. BLOG GENERATION
   When user wants to create a blog, delegate to blog_writer with their mode preference.

   Examples that trigger blog generation:
   - "Write a blog about [topic]"
   - "Create content on [topic]"
   - "I want to write about [topic]"

3. MAINTAIN CONTEXT
   - Remember which mode they chose
   - Keep track of the current blog content
   - Maintain conversation history

# YOUR ROLE
You don't write blogs. You coordinate:
- Capture mode preference
- Route to blog_writer
- Store the generated blog
- Ready for future agents (edit, shortform, multipart)

Keep conversations natural and helpful.
""",
    tools=[blog_writer],
)

# Export root agent for ADK Web
__all__ = ['root_agent']
