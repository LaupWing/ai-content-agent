"""
Root Orchestrator Agent - Multi-Mode Support
Supports both Quick and Thoughtout modes for blog generation
"""

from google.adk.agents import Agent
from prompts.modes.quick_mode import PROMPT as QUICK_PROMPT
from prompts.modes.thoughtout_mode import PROMPT as THOUGHTOUT_PROMPT


def create_blog_writer(mode="quick", model="gemini-2.0-flash-exp"):
    """
    Create a blog writer agent with specified mode

    Args:
        mode: "quick" or "thoughtout"
        model: Gemini model to use

    Returns:
        Agent configured for the specified mode
    """
    if mode == "quick":
        return Agent(
            name="blog_writer_quick",
            model=model,
            description="Fast blog generation - takes topic and immediately creates complete blog",
            instruction=QUICK_PROMPT,
        )
    elif mode == "thoughtout":
        return Agent(
            name="blog_writer_thoughtout",
            model=model,
            description="Interactive blog generation - shows headline options, gathers context, refines iteratively",
            instruction=THOUGHTOUT_PROMPT,
        )
    else:
        raise ValueError(f"Invalid mode: {mode}. Choose 'quick' or 'thoughtout'")


# Default agent (quick mode for backwards compatibility)
root_agent = create_blog_writer(mode="quick")

# Also expose both modes for direct access
quick_agent = create_blog_writer(mode="quick")
thoughtout_agent = create_blog_writer(mode="thoughtout")


# Example usage:
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python agent_with_modes.py [quick|thoughtout] 'your topic'")
        sys.exit(1)

    mode = sys.argv[1]
    topic = sys.argv[2] if len(sys.argv) > 2 else "productivity for remote workers"

    print(f"\nGenerating blog in {mode.upper()} mode...")
    print(f"Topic: {topic}\n")
    print("="*60)

    agent = create_blog_writer(mode=mode)
    response = agent.send_message(topic)

    print(response.content)
    print("\n" + "="*60)
