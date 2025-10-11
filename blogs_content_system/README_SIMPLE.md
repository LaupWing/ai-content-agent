# Blog Content System

Proper ADK multi-agent architecture with session state management.

## Architecture

```
root_agent (blog_orchestrator)
├── Manages session state: mode, blog_content, topic
├── Routes based on mode
│
├─ quick_blog_agent (sub-agent)
│  └─ Fast, one-shot blog generation
│
└─ thoughtout_blog_agent (sub-agent)
   └─ Interactive, step-by-step generation
```

## How It Works (ADK Way)

### 1. Session State
```python
# State stored in session:
{
  "mode": "quick" or "thoughtout",
  "blog_content": "...",
  "topic": "..."
}
```

### 2. Agent Flow
```
User: "Write a blog about productivity"
  ↓
Root checks state: is mode set?
  ↓ (if not set)
Root: "Quick mode or Thoughtout mode?"
  ↓
User: "Quick"
  ↓
Root sets state: mode = "quick"
  ↓
Root transfers to quick_blog_agent
  ↓
Quick agent generates blog
  ↓
Root stores result in state
  ↓
User gets blog
```

### 3. No Prompt Injection
❌ **Bad (old way):** Injecting prompts into one agent
✅ **Good (ADK way):** Two sub-agents, root routes via state

## File Structure

```
blogs_content_system/
├── agent.py                      # Root + sub-agents
├── prompts/
│   ├── modes/
│   │   ├── quick_mode.py        # Quick agent instructions
│   │   └── thoughtout_mode.py   # Thoughtout agent instructions
│   └── archive/                 # Manual versioning
└── AGENT_ARCHITECTURE.md        # Design reference
```

## Usage

### Start ADK Web UI

```bash
adk web agent.py
```

### Test Flow

**First Message:**
```
Write a blog about productivity
```

**Root Agent Response:**
```
Quick mode (fast, I decide everything) or Thoughtout mode (interactive, you guide the direction)?
```

**You Choose:**
```
Quick
```

**What Happens:**
1. Root sets `state["mode"] = "quick"`
2. Root transfers to `quick_blog_agent`
3. Quick agent generates blog immediately
4. Root stores blog in `state["blog_content"]`
5. You get complete blog

**Next Request in Same Session:**
```
Write another blog about goals
```

**What Happens:**
1. Root checks state: mode is already "quick"
2. Root transfers directly to `quick_blog_agent`
3. No need to ask for mode again!

## Key ADK Concepts Used

### Sub-Agents
```python
root_agent = Agent(
    name="blog_orchestrator",
    sub_agents=[quick_blog_agent, thoughtout_blog_agent]
)
```

### State Management
```python
# Root agent instructions mention:
ctx.session.state.get("mode")
ctx.session.state["mode"] = "quick"
```

### Transfer to Sub-Agent
```python
# Root agent will call:
transfer_to_agent("quick_blog_writer")
# or
transfer_to_agent("thoughtout_blog_writer")
```

## Why This Structure?

### ✅ Proper ADK Pattern
- Sub-agents registered with parent
- State managed via session
- Clean separation of concerns

### ✅ Each Agent Has One Job
- `quick_blog_agent`: Generate fast
- `thoughtout_blog_agent`: Generate interactively
- `root_agent`: Route and coordinate

### ✅ Scalable
Easy to add more agents later:
```python
root_agent = Agent(
    name="blog_orchestrator",
    sub_agents=[
        quick_blog_agent,
        thoughtout_blog_agent,
        edit_agent,           # Add later
        shortform_agent,      # Add later
        multipart_agent       # Add later
    ]
)
```

### ✅ State Persists
Mode choice persists across conversation:
```
User: "Write about productivity" → Chooses quick mode
User: "Write about goals"        → Uses quick mode (remembered)
User: "Write about habits"        → Uses quick mode (still remembered)
```

## Testing Tips

### Test Mode Persistence
```
1. Start new session
2. "Write blog about productivity"
3. Choose "Quick"
4. Blog generates
5. "Write blog about goals"
6. Should NOT ask for mode again
```

### Test Sub-Agent Routing
```
1. New session
2. "Write blog about X"
3. Choose "Thoughtout"
4. Should transfer to thoughtout_blog_agent
5. Should show 5 headline options
```

### Check State in ADK Web UI
ADK Web should show session state in the UI (look for state panel)

## Troubleshooting

**Root agent not asking for mode:**
- Check root agent instructions
- Make sure it checks state first

**Root agent not transferring to sub-agent:**
- Check sub_agents list is correct
- Verify agent names match

**Mode not persisting:**
- Check state is being set: `ctx.session.state["mode"] = "quick"`
- Verify same session (not creating new session)

**Sub-agent not generating:**
- Check prompts in `prompts/modes/`
- Test sub-agent individually if needed

## Next Steps

Once this works:
1. ✅ Test both modes thoroughly
2. ⏳ Add edit_agent as sub-agent
3. ⏳ Add shortform_agent for tweets
4. ⏳ Add multipart_agent for threads

## Current Status

✅ Root orchestrator with state management
✅ Two sub-agents (quick, thoughtout)
✅ Proper ADK architecture
⏳ Edit agent (not yet)
⏳ Derivative agents (not yet)
