"""
Section Loop Handler - Custom Agent with Programmatic Loop
This creates a custom ADK agent that loops through sections programmatically
instead of relying on instruction-based iteration.
"""
from typing import AsyncGenerator
from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event


class SectionLoopAgent(BaseAgent):
    """
    Custom agent that programmatically loops through sections.
    Much more reliable than LoopAgent with instruction-based iteration.
    """

    def __init__(self, name: str, researcher_agent):
        super().__init__(name=name, sub_agents=[researcher_agent])
        self.researcher = researcher_agent

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        """
        Programmatically loop through all sections and research each one.

        Reads from ctx.session.state["sections"]
        Writes to ctx.session.state["researched_sections"]
        """

        # Get sections from state
        sections = ctx.session.state.get("sections", [])

        if not sections:
            yield Event.create_text_event(
                "Error: No sections found in state. Planner must run first."
            )
            return

        # Initialize researched sections array
        researched_sections = []

        # Loop through each section
        for idx, section in enumerate(sections):
            section_title = section.get("title", "")
            section_description = section.get("description", "")

            # Inform about progress
            yield Event.create_text_event(
                f"Researching section {idx + 1}/{len(sections)}: {section_title}"
            )

            # Create research prompt for this specific section
            research_prompt = f"""
Research this newsletter section using Google Search:

Title: {section_title}
Description: {section_description}

Use Google Search to find:
- Recent information and statistics
- Relevant hyperlinks and sources
- Key insights and data points

Return your findings as structured JSON.
"""

            # Call researcher sub-agent for this section
            async for event in self.researcher.run_async(ctx, message=research_prompt):
                # Capture the researcher's response
                if event.type == "text":
                    # Store the research result
                    researched_sections.append({
                        "section_title": section_title,
                        "section_description": section_description,
                        "research": event.text
                    })

                # Forward events to maintain visibility
                yield event

        # Save all researched sections to state
        ctx.session.state["researched_sections"] = researched_sections

        # Summary message
        yield Event.create_text_event(
            f"✓ Completed research for {len(researched_sections)} sections"
        )
