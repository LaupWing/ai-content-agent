# Newsletter Agent

A multi-agent system built with Google ADK (Agent Development Kit) for creating high-quality newsletters tailored to specific topics, tones, and target audiences.

## Overview

The Newsletter Agent uses a coordinator pattern with specialized sub-agents to research, write, and format professional newsletters. It follows the same architecture as the workout_coach_agent in this repository.

## Architecture

### Multi-Agent Coordinator Pattern

```
newsletter_coordinator (root coordinator)
├── researcher  - Research & insights specialist
├── writer      - Content writing specialist
└── formatter   - Newsletter formatting specialist
```

**Key architectural points:**
- Root agent (`agent.py`) coordinates by routing to sub-agents via `AgentTool`
- Each sub-agent is self-contained in `sub_agents/{name}/` with `agent.py` and `prompt.py`
- All agents use `gemini-2.5-flash` model
- Sequential workflow: research → write → format

### Agent Responsibilities

- **researcher**: Gathers information, insights, and key points about the newsletter topic
- **writer**: Creates engaging newsletter content tailored to the specified tone and target audience
- **formatter**: Structures and formats the final newsletter for professional presentation

### Workflow

1. User provides topic, tone, and target audience
2. Root coordinator routes to `researcher` agent to gather insights
3. Research findings are passed to `writer` agent to create content
4. Written content is passed to `formatter` agent for final formatting
5. Completed newsletter is delivered to the user

## Getting Started

### Running the Agent

From the parent directory (ai_content_agent/):

```bash
google-adk api-server newsletter_agent
```

The ADK api-server automatically discovers `root_agent` exported from `agent.py`.

### Dependencies

Install from parent directory:
```bash
pip install -r requirements.txt
```

Core dependencies: `google-adk`

## Usage Examples

### Basic Newsletter Creation

**Input:**
```
Create a newsletter about AI productivity tools for tech executives in a professional tone
```

**Process:**
1. Researcher gathers insights about AI productivity tools
2. Writer creates professional content for tech executives
3. Formatter structures the final newsletter
4. Output: Complete, formatted newsletter ready to send

### Custom Requirements

**Input:**
```
Write a newsletter about remote work for startup founders. Keep it casual and actionable.
```

**Process:**
1. Researcher identifies key remote work insights
2. Writer adapts casual tone for startup audience
3. Formatter ensures scannable, action-oriented structure
4. Output: Casual, actionable newsletter for founders

## File Structure

```
newsletter_agent/
├── agent.py              # Root coordinator agent definition
├── prompt.py             # Root agent instructions
├── README.md             # This file
└── sub_agents/
    ├── researcher/       # Research & insights specialist
    │   ├── __init__.py
    │   ├── agent.py
    │   └── prompt.py
    ├── writer/           # Content writing specialist
    │   ├── __init__.py
    │   ├── agent.py
    │   └── prompt.py
    └── formatter/        # Newsletter formatting specialist
        ├── __init__.py
        ├── agent.py
        └── prompt.py
```

## Key Features

### 1. Research-Driven Content
- Gathers relevant information and insights before writing
- Identifies compelling angles and hooks
- Ensures factual, valuable content

### 2. Tone & Audience Adaptation
- Supports multiple tones: professional, casual, friendly, authoritative
- Tailors content for specific audiences: executives, developers, general readers
- Adapts style and complexity accordingly

### 3. Professional Formatting
- Clean, scannable structure
- Proper use of headings, bullets, and emphasis
- Multiple format options: Markdown, HTML, Plain Text
- Mobile-friendly layout

### 4. Quality Assurance
- Structured workflow ensures quality at each stage
- Specialist agents focus on their domain expertise
- Coordinator maintains overall quality and flow

## Customization

### Adding New Sub-Agents

To add a new specialist agent (e.g., fact-checker, editor):

1. Create directory: `sub_agents/{agent_name}/`
2. Add `__init__.py`, `agent.py`, `prompt.py`
3. Define the agent in `agent.py`:
```python
from google.adk.agents import Agent
from . import prompt

your_agent = Agent(
    name="your_agent_name",
    model="gemini-2.5-flash",
    instruction=prompt.YOUR_PROMPT,
    description="What this agent does",
    tools=[]
)
```
4. Import and add to root agent's tools in `newsletter_agent/agent.py`:
```python
from .sub_agents.your_agent.agent import your_agent

tools=[
    AgentTool(agent=researcher),
    AgentTool(agent=writer),
    AgentTool(agent=formatter),
    AgentTool(agent=your_agent),  # Add here
]
```

### Modifying Prompts

Each agent's behavior is defined in its `prompt.py` file:
- `newsletter_agent/prompt.py` - Root coordinator instructions
- `sub_agents/researcher/prompt.py` - Research specialist instructions
- `sub_agents/writer/prompt.py` - Writing specialist instructions
- `sub_agents/formatter/prompt.py` - Formatting specialist instructions

Edit these files to customize agent behavior, add new capabilities, or refine output quality.

## Tone Options

The writer agent supports various tones:

- **Professional**: Data-driven, authoritative, business-focused
- **Casual/Friendly**: Conversational, relatable, warm
- **Authoritative**: Expert insights, thought leadership
- **Conversational**: Like talking to a smart friend

## Audience Targeting

Newsletters can be tailored for:

- Tech executives
- Software developers
- Marketing professionals
- Startup founders
- General readers
- Industry specialists
- Community members

## Output Formats

The formatter agent can deliver newsletters in:

- **Markdown** (default): Clean, portable, easy to edit
- **HTML**: Ready for email clients
- **Plain Text**: Maximum compatibility

## Best Practices

1. **Be Specific**: Provide clear topic, tone, and audience requirements
2. **Iterate**: Request revisions if needed - agents can refine output
3. **Test Tones**: Try different tones for the same topic to find what works
4. **Review Research**: Ensure research phase captures the right insights
5. **Formatting**: Specify format preference (Markdown/HTML/Text) if needed

## Example Output

**Input:** "Create a newsletter about AI productivity for tech leaders in a professional tone"

**Output:**
```markdown
# The AI Productivity Paradox—And How to Solve It

The data is clear: companies implementing AI tools see a 40% increase in
output. But here's what the reports don't tell you—**60% of those same
companies report employee burnout is up.**

The issue isn't AI itself. It's implementation without strategy.

## Three Patterns That Separate High Performers

### 1. Clear Human-AI Role Definition
Successful teams define what AI handles and what humans own...

### 2. Protected Deep Work Time
Top performers block 40% of their calendar...

### 3. Output Quality Metrics
Leading teams measure impact per project...

---

**The Bottom Line**: Speed without strategy gets you to burnout faster.

What are you optimizing for?
```

## Troubleshooting

**Issue**: Agent doesn't understand requirements
- **Solution**: Be more specific about topic, tone, and audience

**Issue**: Content doesn't match desired tone
- **Solution**: Explicitly specify tone in the request ("professional tone", "casual and friendly")

**Issue**: Newsletter too long/short
- **Solution**: Specify length preference ("brief update", "detailed analysis")

**Issue**: Formatting issues
- **Solution**: Specify desired format (Markdown/HTML/Plain Text)

## Contributing

To improve the newsletter agent:

1. Review prompt files for each specialist agent
2. Test with various topics, tones, and audiences
3. Refine prompts based on output quality
4. Add new specialist agents as needed
5. Update this README with new features

## License

Same as parent project.
