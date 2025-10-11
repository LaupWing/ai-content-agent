# Multi-Agent Architecture for Blog System

## Overview

This system uses Google ADK's agent orchestration to manage blog creation and derivative content within a single session.

## Core Concept

```
ONE SESSION = ONE BLOG PROJECT

User starts session → Chooses mode → Blog created → Can edit/create derivatives
                      (quick/thoughtout)      (stays in same session)
```

---

## Recommended Architecture

### Option 1: Root Orchestrator (RECOMMENDED)

```
┌─────────────────────────────────────────────────────────────┐
│                    ROOT ORCHESTRATOR                         │
│  (Always active, routes to specialized agents)              │
└────────────────────────┬────────────────────────────────────┘
                         │
          ┌──────────────┼──────────────┬──────────────┐
          │              │              │              │
          ▼              ▼              ▼              ▼
    ┌─────────┐    ┌─────────┐   ┌──────────┐   ┌──────────┐
    │  BLOG   │    │  EDIT   │   │  SHORT   │   │  MULTI   │
    │ WRITER  │    │  AGENT  │   │  FORM    │   │  PART    │
    │         │    │         │   │  AGENT   │   │  AGENT   │
    └─────────┘    └─────────┘   └──────────┘   └──────────┘
         │
    ┌────┴────┐
    │  MODE   │
    │ CONTEXT │
    │(quick or│
    │thought) │
    └─────────┘
```

**How it works:**

```python
# Root Orchestrator (agent.py)
root_agent = Agent(
    name="blog_orchestrator",
    instruction="""You coordinate blog creation and editing.

    When user first arrives:
    - Ask: "Quick mode (fast) or Thoughtout mode (interactive)?"
    - Store their choice in session context

    Then delegate to appropriate agent:
    - Blog generation → blog_writer (with mode context)
    - Editing → edit_agent
    - Tweet creation → shortform_agent
    - Thread creation → multipart_agent

    Maintain conversation context across all agents.
    """,
    tools=[
        blog_writer,
        edit_agent,
        shortform_agent,
        multipart_agent
    ]
)
```

**Session Flow:**

```
User: "I want to write a blog about productivity"

Root: "Quick mode (fast) or Thoughtout mode (step-by-step)?"

User: "Thoughtout"

Root: [Delegates to blog_writer with mode="thoughtout"]
BlogWriter: "I can take this in 5 directions: [headlines]"

User: "Option 2"

BlogWriter: [Generates blog]

User: "Make the intro more casual"

Root: [Delegates to edit_agent]
EditAgent: [Edits intro, returns updated blog]

User: "Now create a thread from this"

Root: [Delegates to multipart_agent]
MultiPartAgent: [Creates 7-tweet thread]

# All in ONE session, context maintained
```

---

### Option 2: Sequential HandOffs (Your Original Idea)

```
Step 1: Choose Mode
  ↓
Step 2: BlogWriter Agent (generates)
  ↓ [HandOff]
Step 3: EditAgent (if user wants edits)
  ↓ [HandOff]
Step 4: ShortForm/MultiPart Agent (derivatives)
```

**Problems with this approach:**
- ❌ Rigid flow (what if user wants to edit THEN create thread?)
- ❌ HandOffs break context
- ❌ User has to explicitly trigger each handoff
- ❌ Can't go back to previous agent easily

---

## Detailed Agent Breakdown

### 1. Root Orchestrator Agent

**File:** `agent.py` (replace current)

**Responsibilities:**
- Greet user
- Capture mode preference (quick/thoughtout) ONCE at start
- Route requests to appropriate specialized agent
- Maintain blog state across agents
- Handle conversational context

**Instructions:**
```python
ORCHESTRATOR_INSTRUCTIONS = """
You are the Blog Project Coordinator.

# SESSION CONTEXT
Each session represents ONE blog project. Context persists across all agents.

# FIRST INTERACTION
When user starts, ask:
"Quick mode (I'll generate fast) or Thoughtout mode (we'll work step-by-step)?"

Store their choice. Use it when calling blog_writer.

# ROUTING RULES

Route to blog_writer when user wants:
- "Write a blog about [topic]"
- "Create blog post on [topic]"
- "Generate content about [topic]"

Route to edit_agent when user wants:
- "Edit the [section]"
- "Make [part] more [style]"
- "Rewrite the [section]"
- "Change the tone"

Route to shortform_agent when user wants:
- "Create a tweet"
- "Turn this into a tweet"
- "Give me social media post"

Route to multipart_agent when user wants:
- "Create a thread"
- "Break this into tweets"
- "Make a Twitter thread"

# CONTEXT PASSING
Always pass:
- Current blog content
- User's mode preference
- Any previous edits

# CONVERSATION FLOW
User can jump between agents naturally:
"Write blog" → "Edit intro" → "Create thread" → "Edit tweet 3" → etc.

You maintain context across all transitions.
"""
```

---

### 2. Blog Writer Agent

**File:** `agents/blog_writer.py`

**Responsibilities:**
- Generate initial blog
- Handle BOTH quick and thoughtout modes via context
- Return complete blog content

**Key Point:** ONE agent, not two. Mode is a parameter.

**Instructions:**
```python
BLOG_WRITER_INSTRUCTIONS = """
You generate blog content.

# MODE HANDLING

If mode == "quick":
- Take topic directly
- Generate complete blog immediately
- No questions, no options

If mode == "thoughtout":
- Show 5 headline options
- Ask for context (optional)
- Generate after user chooses

# OUTPUT
Return complete blog with:
- Headline
- Body (1500-2500 words)
- Structured with markdown

# CONTEXT AWARENESS
You're part of a larger session. After you generate the blog,
user might want to edit it or create derivatives. That's not
your job - just generate the initial blog well.
"""
```

**Implementation:**
```python
blog_writer = Agent(
    name="blog_writer",
    model="gemini-2.0-flash-exp",
    instruction=BLOG_WRITER_INSTRUCTIONS,
)
```

---

### 3. Edit Agent

**File:** `agents/edit_agent.py`

**Responsibilities:**
- Modify specific sections of existing blog
- Adjust tone, length, style
- Rewrite sections while maintaining context

**Instructions:**
```python
EDIT_AGENT_INSTRUCTIONS = """
You edit existing blog content.

# CONTEXT
You receive:
- The current blog (full content)
- User's edit request ("make intro more casual")

# CAPABILITIES
You can:
- Rewrite specific sections
- Adjust tone (more casual, more professional, more provocative)
- Expand or shorten sections
- Add or remove examples
- Change headline

# RULES
- Only change what user requests
- Maintain overall blog structure
- Don't introduce new topics
- Match existing style unless asked to change it

# OUTPUT
Return:
- Updated blog (full content with edits)
- Summary of what you changed
"""
```

**Why separate from BlogWriter?**
- Different skill: creation vs refinement
- Can focus prompts specifically on editing
- User mental model: "I'm editing now" (clear transition)

---

### 4. Short Form Agent

**File:** `agents/shortform_agent.py`

**Responsibilities:**
- Extract key points from blog
- Create single tweets/posts
- Adapt to platform (Twitter, LinkedIn, etc.)

**Instructions:**
```python
SHORTFORM_AGENT_INSTRUCTIONS = """
You create short-form content from blogs.

# INPUT
- Blog content (full)
- Platform (Twitter, LinkedIn, etc.)
- Optional: specific angle user wants

# CAPABILITIES
Create:
- Single tweet (280 chars)
- LinkedIn post (1300 chars)
- Instagram caption
- Facebook post

# EXTRACTION STRATEGY
1. Identify core insight from blog
2. Find most compelling hook
3. Condense to platform limits
4. Maintain voice and impact

# OUTPUT
Return:
- Short-form content
- Character count
- Reasoning (which insight you extracted)
"""
```

---

### 5. Multi-Part Agent

**File:** `agents/multipart_agent.py`

**Responsibilities:**
- Break blog into thread (5-10 tweets)
- Maintain narrative flow
- Create hooks between parts

**Instructions:**
```python
MULTIPART_AGENT_INSTRUCTIONS = """
You create multi-part content (threads) from blogs.

# INPUT
- Blog content (full)
- Platform (Twitter thread, LinkedIn carousel, etc.)
- Optional: desired length (5 tweets, 10 tweets)

# THREAD STRUCTURE

Tweet 1 (Hook):
- Grab attention
- Promise value
- No fluff

Tweet 2-N (Content):
- One idea per tweet
- Build on previous
- Use numbers/bullets

Tweet N (CTA):
- Summarize value
- Clear next step
- Engagement prompt

# RULES
- Each tweet stands alone but flows together
- Maintain consistent voice
- End tweets with transitions ("Here's why:")
- Use thread best practices (hooks, white space, emojis)

# OUTPUT
Return:
- Array of tweets with content
- Tweet count
- Flow explanation
"""
```

---

## State Management

### Session State

```python
class BlogSession:
    session_id: str
    mode: str  # "quick" or "thoughtout"
    blog_content: str | None
    headline: str | None
    edit_history: List[Edit]
    derivatives: List[Derivative]
    created_at: datetime
    updated_at: datetime

# Example session progression:
{
  "session_id": "sess_123",
  "mode": "thoughtout",
  "blog_content": "[full blog content]",
  "headline": "Why 92% of Goals Fail",
  "edit_history": [
    {"agent": "edit", "request": "make intro casual", "timestamp": "..."}
  ],
  "derivatives": [
    {"type": "tweet", "content": "...", "created_at": "..."},
    {"type": "thread", "tweets": [...], "created_at": "..."}
  ]
}
```

### Passing Context Between Agents

```python
# Root orchestrator maintains state
root_agent.context = {
    "mode": "thoughtout",
    "current_blog": "[blog content]",
    "session": blog_session
}

# When delegating:
blog_writer.receive_context(root_agent.context)
edit_agent.receive_context(root_agent.context)
# etc.
```

---

## User Experience Examples

### Example 1: Full Flow

```
User: "I want to write about productivity"

Root: "Quick mode (fast) or Thoughtout mode (step-by-step)?"

User: "Thoughtout"

Root → BlogWriter(thoughtout):
BlogWriter: "I can take this in 5 directions:
  1. Personal: I Failed at Productivity for 10 Years...
  2. Contrarian: Why Productivity Advice Is Making You Less Productive
  3. Data: 87% of Productivity Tips Don't Work. Here Are the 3 That Do
  4. Framework: The 3-Phase Productivity System
  5. List: 7 Productivity Habits That Actually Work
Which direction?"

User: "Option 2"

BlogWriter: "Want to add context or should I go?"

User: "I work from home and get distracted easily"

BlogWriter: [Generates 2000-word blog about why common productivity advice fails, tailored to remote work]

User: "Make the conclusion stronger"

Root → EditAgent:
EditAgent: [Rewrites conclusion with stronger call-to-action]

User: "Now create a thread from this"

Root → MultiPartAgent:
MultiPartAgent: [Creates 8-tweet thread summarizing key points]

User: "Change tweet 3 to be more casual"

Root → EditAgent(for derivative):
EditAgent: [Edits tweet 3]

User: "Perfect, export everything"

Root: [Provides blog + thread in exportable format]
```

### Example 2: Quick Mode → Derivatives

```
User: "Write blog about goal setting, quick mode"

Root → BlogWriter(quick):
BlogWriter: [Generates complete blog immediately, ~60 seconds]

User: "Good. Create 3 tweets from this"

Root → ShortFormAgent:
ShortFormAgent:
  Tweet 1: [Hook about goal failure]
  Tweet 2: [Key insight]
  Tweet 3: [Call to action]

User: "Done"
```

---

## Implementation Approach

### Phase 1: Root + Blog Writer (This Week)

```python
# agent.py
from google.adk.agents import Agent
from agents.blog_writer import blog_writer

root_agent = Agent(
    name="blog_orchestrator",
    instruction=ORCHESTRATOR_INSTRUCTIONS,
    tools=[blog_writer]
)
```

**Test:**
- User can choose mode
- Blog generation works in both modes
- Context persists in session

### Phase 2: Add Edit Agent (Next Week)

```python
from agents.edit_agent import edit_agent

root_agent = Agent(
    name="blog_orchestrator",
    instruction=ORCHESTRATOR_INSTRUCTIONS,
    tools=[blog_writer, edit_agent]
)
```

**Test:**
- User can edit after generation
- Multiple edits work
- Context maintained

### Phase 3: Add Derivative Agents (Week 3)

```python
from agents.shortform_agent import shortform_agent
from agents.multipart_agent import multipart_agent

root_agent = Agent(
    name="blog_orchestrator",
    instruction=ORCHESTRATOR_INSTRUCTIONS,
    tools=[blog_writer, edit_agent, shortform_agent, multipart_agent]
)
```

**Test:**
- Derivatives extract correctly from blog
- Can edit derivatives
- Full flow works end-to-end

---

## Key Decisions

### 1. One BlogWriter or Two?

**Recommendation:** ONE agent with mode as context

**Rationale:**
- Same core capability (writing)
- Reduces maintenance
- ADK handles conditional behavior well
- Can add more modes later easily

### 2. When to Create Derivatives?

**Option A:** Automatically after blog
- ❌ User might not want them
- ❌ Extra cost
- ❌ Slower generation

**Option B:** On-demand (RECOMMENDED)
- ✅ User chooses
- ✅ Faster initial generation
- ✅ Lower cost
- ✅ More control

### 3. State Persistence?

**For MVP:** In-memory session state (ADK handles)

**For Production:** Database-backed
```python
# Store in your MySQL/Postgres
class AgentSession(Model):
    id: int
    user_id: int
    mode: str
    context: JSON
    blog_content: TEXT
    created_at: datetime
```

---

## File Structure

```
blogs_content_system/
├── agent.py                      # Root orchestrator
├── prompts/
│   ├── orchestrator.py          # Root instructions
│   ├── blog_writer.py           # Blog generation (both modes)
│   ├── edit_agent.py            # Editing instructions
│   ├── shortform_agent.py       # Tweet/post generation
│   └── multipart_agent.py       # Thread generation
├── agents/
│   ├── __init__.py
│   ├── blog_writer.py           # Blog writer agent instance
│   ├── edit_agent.py            # Editor agent instance
│   ├── shortform_agent.py       # Short-form agent instance
│   └── multipart_agent.py       # Multi-part agent instance
└── testing/
    └── test_full_flow.py        # End-to-end tests
```

---

## Summary: My Opinion

### ✅ What You Got Right

1. **Session-based**: Each blog = one session ✅
2. **Specialized agents**: Each agent does one thing ✅
3. **Mode choice at start**: Quick vs Thoughtout ✅
4. **Linear progression**: Blog → Edit → Derivatives makes sense ✅

### 🔄 What I'd Change

1. **ONE BlogWriter agent** (not two)
   - Mode is just a parameter/context
   - Easier to maintain

2. **Root Orchestrator pattern** (not sequential handoffs)
   - More flexible
   - Better UX
   - Easier to navigate

3. **On-demand derivatives** (not automatic)
   - User chooses when
   - Lower cost
   - Faster

### 🎯 Recommended Next Steps

1. **This week:** Build root orchestrator + blog writer
2. **Next week:** Add edit agent
3. **Week 3:** Add derivative agents
4. **Week 4:** Test full flow, optimize

This architecture gives you:
- ✅ Flexibility (user can jump between any agent)
- ✅ Simplicity (one root agent coordinates)
- ✅ Scalability (easy to add more agents)
- ✅ Clear separation (each agent has one job)

Want me to implement this architecture?
