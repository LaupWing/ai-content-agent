# Blog Content System

Simple multi-agent blog writer with Quick and Thoughtout modes.

## File Structure

```
blogs_content_system/
├── agent.py                      # Root orchestrator (start here)
├── prompts/
│   ├── modes/
│   │   ├── quick_mode.py        # Quick mode prompt
│   │   └── thoughtout_mode.py   # Thoughtout mode prompt
│   └── archive/                 # Manual archiving (when you iterate)
└── AGENT_ARCHITECTURE.md        # System design reference
```

## How to Use

### 1. Start ADK Web UI

```bash
adk web agent.py
```

This opens the UI at `http://localhost:8000` (or whatever port ADK uses)

### 2. Test in the UI

**First message:**
```
Write a blog about productivity
```

**Agent will ask:**
```
Quick mode (fast) or Thoughtout mode (step-by-step)?
```

**You respond:**
```
Quick
```
or
```
Thoughtout
```

### 3. Expected Behavior

**Quick Mode:**
- Agent generates complete blog immediately
- No questions, just delivers

**Thoughtout Mode:**
- Agent shows 5 headline options
- You choose one
- Agent asks for optional context
- Then generates blog

## How It Works

```
root_agent (orchestrator)
  └─ blog_writer (handles both modes)
```

1. Root agent asks for mode preference
2. Root agent delegates to blog_writer with mode context
3. Blog writer generates based on mode
4. Context maintained in session

## Making Changes

### Update Prompts

Edit these files:
- `prompts/modes/quick_mode.py`
- `prompts/modes/thoughtout_mode.py`

### Archive Old Version

When you want to save a version:
```bash
cp prompts/modes/quick_mode.py prompts/archive/quick_mode_v1_YYYYMMDD.py
```

Then edit the current version.

### Test Changes

Just restart ADK Web:
```bash
# Ctrl+C to stop
adk web agent.py
```

New session will use updated prompts.

## Next Steps

Once blog generation works:

1. **Add Edit Agent** (see AGENT_ARCHITECTURE.md)
2. **Add ShortForm Agent** (tweets)
3. **Add MultiPart Agent** (threads)

But test blog generation first!

## Troubleshooting

**Agent doesn't call blog_writer:**
- Check root_agent instructions
- Make sure you're asking for blog generation

**Wrong mode used:**
- Check conversation context
- Root agent should capture mode choice

**Prompts too long:**
- ADK might truncate
- Check model context limits

## Current Status

✅ Root orchestrator
✅ Blog writer (both modes)
⏳ Edit agent (not yet)
⏳ ShortForm agent (not yet)
⏳ MultiPart agent (not yet)
