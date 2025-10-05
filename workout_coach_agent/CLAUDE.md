# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **multi-agent workout coaching system** built with Google ADK (Agent Development Kit). The system uses a coordinator pattern where a root agent (`workout_coach`) routes user requests to five specialized sub-agents, each handling distinct fitness coaching domains.

## Architecture

### Multi-Agent Coordinator Pattern

The system follows a hierarchical agent architecture:

```
workout_coach (root coordinator)
├── logger     - Workout logging specialist
├── planner    - Workout planning specialist
├── analyst    - Progress analysis specialist
├── exercise   - Form/technique specialist
└── hype       - Motivation specialist
```

**Key architectural points:**
- Root agent (`agent.py`) coordinates by routing to sub-agents via `AgentTool`
- Each sub-agent is self-contained in `sub_agents/{name}/` with `agent.py` and `prompt.py`
- User context (user_id, session state) flows through `ToolContext` automatically
- All agents use `gemini-2.5-flash` model
- Backend integration via Laravel API through `tools.py`

### Agent Responsibilities

- **logger**: Parses natural language workout descriptions and logs to database via `log_workout()` tool
- **planner**: Prescribes daily workouts using `get_todays_workout()` and `get_active_workout_plan()` tools
- **analyst**: Analyzes progress using `get_workout_history()` and `get_workout_summary()` tools
- **exercise**: Teaches form/technique using `search_exercises()` tool to query exercise database
- **hype**: Pure motivation agent with no tools, just encouragement

### Data Flow

1. User request → `workout_coach` (root)
2. Root agent analyzes intent → routes to specialist
3. Specialist calls tools → `_make_laravel_request()` in `tools.py`
4. Laravel API returns data → specialist processes → response to user
5. `ToolContext.state` contains `user_id` automatically injected

## Development Commands

### Running the Agent

```bash
# From parent directory (ai_content_agent/)
google-adk api-server workout_coach_agent
```

The ADK api-server automatically discovers `root_agent` exported from `agent.py`.

### Environment Setup

Create `.env` file with:
```
LARAVEL_API_URL=http://localhost:8001/api
LARAVEL_API_KEY=your_api_key_here
```

### Dependencies

Install from parent directory:
```bash
pip install -r requirements.txt
```

Core dependencies: `google-adk`, `httpx`, `python-dotenv`

## Working with Sub-Agents

### Adding a New Sub-Agent

1. Create directory: `sub_agents/{agent_name}/`
2. Add `__init__.py`, `agent.py`, `prompt.py`
3. Define tools as functions with `ToolContext` parameter
4. Create agent instance with name, model, instruction, tools
5. Import and add `AgentTool(agent=your_agent)` to root agent's tools list

### Tool Function Pattern

```python
def your_tool(tool_context: ToolContext, param: str) -> Dict:
    user_id = tool_context.state.get("user_id")
    # Your logic here
    return _make_laravel_request("POST", "endpoint", data)
```

### Prompt Files

Located in `sub_agents/{name}/prompt.py` as module-level string constants (e.g., `LOGGER_PROMPT`, `PLANNER_PROMPT`). These contain detailed instructions for each specialist agent's behavior and domain expertise.

## Laravel API Integration

All backend communication goes through `tools.py`:
- `_make_laravel_request(method: str, endpoint: str, data: Optional[Dict])`
- Handles auth headers, error handling, logging
- Endpoints: `workouts/log`, `workouts/history`, `workout-plans/today`, `exercises/search`, etc.

**Note**: Currently hardcoded bearer token (`Bearer xx`) on line 13 of `tools.py` - this should use `LARAVEL_API_KEY` from environment.

## File Structure

```
workout_coach_agent/
├── agent.py           # Root coordinator agent definition
├── prompt.py          # Root agent instructions
├── tools.py           # Shared Laravel API helper
├── config.py          # Empty config file
└── sub_agents/
    ├── logger/        # Workout logging
    ├── planner/       # Daily workout prescription
    ├── analyst/       # Progress tracking
    ├── exercise/      # Form coaching
    └── hype/          # Motivation
```

Each sub-agent directory contains `agent.py` (agent + tools) and `prompt.py` (instructions).
