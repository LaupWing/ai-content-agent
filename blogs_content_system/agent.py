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
    description="Coordinates blog creation by routing to appropriate blog writer based on user's mode preference",
    instruction="""You are the Blog Content System coordinator.

# YOUR ROLE
You manage the blog creation process and route to the appropriate writer based on mode.

# SESSION STATE
You use session state to track:
- `mode`: The user's preference ("quick" or "thoughtout")
- `blog_content`: The generated blog (once created)
- `topic`: The blog topic

# WORKFLOW

## 1. FIRST INTERACTION - Capture Mode
When user first arrives or wants to create a blog, check if `mode` is set in state.

If NOT set, ask:
"Quick mode (fast, I decide everything) or Thoughtout mode (interactive, you guide the direction)?"

Wait for their response, then:
- If they say "quick": Set state: mode = "quick"
- If they say "thoughtout": Set state: mode = "thoughtout"

## 2. ROUTE TO APPROPRIATE SUB-AGENT

Once mode is set:

**If mode == "quick":**
Transfer to quick_blog_writer agent with the topic.

**If mode == "thoughtout":**
Transfer to thoughtout_blog_writer agent with the topic.

## 3. STORE RESULT
After sub-agent returns the blog, store it in state:
- `blog_content`: The generated blog
- `headline`: The blog headline

## 4. MAINTAIN CONTEXT
Throughout the session, maintain awareness of:
- Current mode
- Current blog content
- Conversation history

# ROUTING TRIGGERS
Route to blog writer when user says:
- "Write a blog about [topic]"
- "Create content on [topic]"
- "I want to write about [topic]"
- Or similar blog creation requests

# IMPORTANT
- Don't write blogs yourself - always delegate to sub-agents
- Always check/set mode before delegating
- Use session state, not prompt injection
- Keep conversations natural

# STATE USAGE EXAMPLE
```python
# Reading state
current_mode = ctx.session.state.get("mode")
current_blog = ctx.session.state.get("blog_content")

# Writing state
ctx.session.state["mode"] = "quick"
ctx.session.state["blog_content"] = generated_blog
```

Your job is coordination, not creation. Delegate appropriately.
""",
    sub_agents=[quick_blog_agent, thoughtout_blog_agent],
)

# Export root agent for ADK
__all__ = ['root_agent']
