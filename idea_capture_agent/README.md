# Idea Capture Agent

An intelligent AI agent that captures, processes, and manages your ideas in Notion with automatic title generation, description cleanup, and smart tagging.

## Overview

The Idea Capture Agent is designed with one primary goal: **Make capturing ideas effortless**. Simply blast your raw idea to the agent, and it handles everything else - generating titles, cleaning up descriptions, creating relevant tags, and storing everything in Notion.

## Core Features

### Primary Capability: Smart Idea Capture
- **Input**: Raw, messy idea text in any format
- **Process**: Automatic title generation, description cleanup, and intelligent tag creation
- **Output**: Well-structured idea stored in Notion

### Additional Capabilities
1. **List Ideas**: View all your captured ideas
2. **Query Ideas**: Search by keywords, tags, or date ranges
3. **Update Ideas**: Modify existing ideas
4. **Delete Ideas**: Remove ideas (with confirmation)
5. **Expand Ideas**: Transform brief ideas into detailed descriptions or action plans
6. **Weekly Reports**: Get summaries of your ideas in text or MP3 format

## Architecture

The agent uses a clean, modular architecture:

```
Root Agent (idea_capture)
├── Routing & simple operations (list, query, update, delete)
└── Delegates to specialized agents:
    ├── add_idea_agent (handles 80% of the intelligence)
    │   ├── Title generation
    │   ├── Description cleanup
    │   ├── Tag detection & creation
    │   └── Notion API interaction
    ├── expand_idea_agent (future)
    └── report_agent (future)
```

**Design Philosophy**: Keep the root agent lean and mean. All complex processing is delegated to specialized sub-agents.

## How It Works

### 1. Adding Ideas (Primary Use Case)

User input:
```
"yo we should add dark mode it's annoying at night"
```

Agent processes:
- **Raw Text**: "yo we should add dark mode it's annoying at night"
- **Title**: "Add Dark Mode Feature"
- **Description**: "Implement dark mode to improve user experience during nighttime usage and reduce eye strain."
- **Tags**: ["feature-request", "ui-ux", "accessibility", "quick-win"]

### 2. Managing Ideas

```
List all ideas
Show ideas tagged with "urgent"
Update my dark mode idea
Delete the old feature request
```

### 3. Expanding Ideas

```
Expand my dark mode idea into an action plan
Give me more details on the marketing campaign idea
Show me different variations of the automation concept
```

### 4. Weekly Reports

```
Send me a weekly report grouped by tags
Generate an audio report of this week's ideas
```

## Technical Details

### State Management
- Stateless system - all state managed in Notion
- No persistent memory between requests

### Notion Integration
- Uses Notion page IDs internally for all operations
- Users only see/use idea titles
- Automatic ID resolution when users reference ideas by name

### Error Handling
- User-facing: Simple, clear error messages
- Internal: Full error details captured for debugging

## Project Structure

```
idea_capture_agent/
├── __init__.py
├── agent.py              # Root agent definition
├── prompt.py             # Main agent prompt
├── TODO.md               # Development decisions & roadmap
└── README.md             # This file
```

## Getting Started

1. **Setup Notion Integration**
   - Create a Notion database with fields: Title, Description, Tags, Raw Text, Created Date
   - Configure MCP for Notion API access

2. **Configure the Agent**
   ```python
   from idea_capture_agent import idea_capture

   # Agent is ready to use
   idea_capture.run("I want to build a chrome extension for bookmarking")
   ```

3. **Implement Tools** (TODO)
   - `list_ideas`
   - `query_ideas`
   - `add_idea_agent` (sub-agent)
   - `update_idea`
   - `delete_idea`
   - `expand_idea`
   - `send_weekly_report`

## Development Roadmap

### Phase 1: Core Capture (MVP)
- [ ] Implement root agent
- [ ] Create `add_idea_agent` sub-agent
- [ ] Build basic tools: `add_idea_agent`, `list_ideas`, `query_ideas`
- [ ] Test: User → raw idea → processed → stored

### Phase 2: Management Features
- [ ] Implement `update_idea`
- [ ] Implement `delete_idea`
- [ ] Test full CRUD operations

### Phase 3: Advanced Features
- [ ] Create `expand_idea_agent`
- [ ] Create `report_agent` for weekly reports
- [ ] Implement MP3 generation for audio reports
- [ ] Test end-to-end workflows

## Configuration

See `TODO.md` for detailed configuration decisions needed:
- Tag generation strategy
- Weekly report content & format
- Expansion types and depth
- Notion database schema

## Best Practices

### For Users
- Just blast your idea - don't worry about formatting
- Use natural language to reference ideas ("my dark mode idea")
- Be specific when updating or deleting ideas

### For Developers
- Keep root agent lean - delegate complex logic to sub-agents
- Always use page IDs internally, never expose to users
- Test tag generation thoroughly - it's the most valuable feature
- Error messages should be simple for users, detailed for logs

## Dependencies

- Google ADK (Agent Development Kit)
- Notion API via MCP
- gemini-2.5-flash (model)

## Contributing

When adding features:
1. Check `TODO.md` for architectural decisions
2. Keep root agent minimal
3. Create specialized sub-agents for complex tasks
4. Update prompts to be clear and concise
5. Test with messy, real-world input

## License

[Your License Here]

## Support

For issues, questions, or feature requests, please [create an issue/contact info].
