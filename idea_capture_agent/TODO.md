# Idea Capture Agent - TODO & Decisions Needed

## Architecture Decisions

### 1. Agent Structure - NEEDS DECISION
**Current Thinking:** Create separate `add_idea_agent` to handle 80% of the intelligence
- [ ] Decide: Should `add_idea_agent` be a separate agent or a tool?
- [ ] Define: What exactly does the `add_idea_agent` do?
  - Generate title from raw text?
  - Clean up description?
  - Auto-generate tags based on content analysis?
  - All of the above?
- [ ] Decide: How does root agent communicate with `add_idea_agent`?
  - Does root agent call it as a tool?
  - Does root agent delegate to it?

**Implication:** If using separate agent, root prompt stays LEAN (good practice for Google ADK)

### 2. Tag Generation - NEEDS SPECIFICATION
- [ ] Define tag categories/domains to prioritize
  - Business vs Technical vs Personal?
  - Priority levels (urgent, quick-win, long-term)?
  - Project areas?
- [ ] Decide: How many tags per idea? (suggested 2-5)
- [ ] Define: Tag naming convention (lowercase? hyphens? underscores?)
- [ ] Decide: Should tags be from predefined list or completely dynamic?

### 3. Weekly Report Feature - NEEDS SPECIFICATION
- [ ] Define: What content goes in the weekly report?
  - Just list of idea titles?
  - Include descriptions?
  - Include tag summaries?
  - Include statistics (# ideas by tag, most active tags)?
- [ ] Define: How is it structured?
  - Chronological?
  - Grouped by tags?
  - Prioritized somehow?
- [ ] Decide: MP3 format details
  - Text-to-speech of the report?
  - Who generates the MP3? (this agent or external service?)
  - What voice/style?
- [ ] Decide: Confirmation required before sending?
- [ ] Decide: Where does it send to? (email, slack, download?)

### 4. Expand Idea Feature - NEEDS SPECIFICATION
- [ ] Define: Input format
  - Just idea ID?
  - Or raw text for expansion?
- [ ] Define: What level of expansion?
  - Brief → Detailed description?
  - Brief → Full action plan?
  - Brief → Multiple variations?
- [ ] Decide: Does expansion create NEW idea or UPDATE existing?
- [ ] Decide: Does expansion also re-generate tags?

### 5. Update Idea Feature - NEEDS SPECIFICATION
- [ ] Decide: Can user update individual fields?
  - Update just title?
  - Update just description?
  - Update just tags?
  - All at once?
- [ ] Decide: When user updates, does agent re-process?
  - Re-generate tags automatically?
  - Or keep manual edits?

### 6. Delete Idea Feature - NEEDS SPECIFICATION
- [ ] Decide: Always ask for confirmation?
- [ ] Decide: Soft delete vs hard delete?
- [ ] Decide: Can user undo deletion?

## Prompt Architecture Decisions

### 7. Root Agent Prompt - PHILOSOPHY
**Feedback Received:** "Keep root agent lean and mean, don't over-explain"

- [ ] Decide: How minimal should root prompt be?
  - Just routing logic (which agent/tool to call)?
  - Or include some intelligence?
- [ ] Decide: What goes in root prompt vs sub-agent prompts?
  - **Root:** High-level capabilities, routing, tool usage
  - **Sub-agent (add_idea):** Processing logic, tag generation, title/description creation

### 8. Examples in Prompt - NEEDS DECISION
- [ ] Decide: Include examples in root prompt?
  - Pro: Helps agent understand workflow
  - Con: Makes prompt longer (conflicts with "lean and mean")
- [ ] Decide: If examples, how many?
  - 1 comprehensive example?
  - 2-3 varied examples?
  - None (keep it lean)?

### 9. Tool Definitions - NEEDS COMPLETION
- [ ] Complete: `add_idea` parameters (or reference to sub-agent?)
- [ ] Complete: `update_idea` full definition
- [ ] Complete: `delete_idea` full definition
- [ ] Complete: `expand_idea` full definition
- [ ] Complete: `send_weekly_report` full definition
- [ ] Complete: `query_ideas` full definition (currently incomplete)

## Implementation Order (Suggested)

1. **Phase 1: Core Capture (MVP)**
   - [ ] Complete root agent prompt (lean version)
   - [ ] Create `add_idea_agent` prompt (handles processing)
   - [ ] Implement basic `add_idea` tool
   - [ ] Implement `list_ideas` tool
   - [ ] Implement `query_ideas` tool
   - [ ] Test: User blasts idea → Agent processes → Stored correctly

2. **Phase 2: Management Features**
   - [ ] Implement `update_idea` tool
   - [ ] Implement `delete_idea` tool
   - [ ] Test: Full CRUD operations

3. **Phase 3: Advanced Features**
   - [ ] Implement `expand_idea` tool/agent
   - [ ] Implement `send_weekly_report` tool/agent
   - [ ] Test: End-to-end workflows

## Notion Integration - NEEDS VERIFICATION

- [ ] Confirm: Notion database structure
  - What fields exist? (Title, Description, Tags, Raw Text, Created Date, etc.)
  - Field types? (Title = title type, Tags = multi-select, etc.)
- [ ] Confirm: How to add tags to Notion
  - Create new tags on the fly?
  - Must exist in database first?
- [ ] Confirm: API access and permissions

## Open Questions

1. **User Experience:**
   - [ ] Should agent provide feedback after adding idea? ("Saved! Tagged as X, Y, Z")
   - [ ] Should agent suggest related existing ideas when adding?

2. **Error Handling:**
   - [ ] What if Notion API fails?
   - [ ] What if tag generation fails?
   - [ ] What if idea is too vague to process?

3. **Privacy/Security:**
   - [ ] Any sensitive idea filtering needed?
   - [ ] Should some ideas be private/public?

## My Honest Feedback on Your Approach

### ✅ GREAT IDEA: Separate `add_idea_agent`
**Why this is smart:**
- Root agent stays lean (Google ADK best practice)
- Processing logic is isolated and can be refined independently
- Easy to test and debug tag generation separately
- Can swap out processing strategies without touching root agent
- 80% of complexity lives in one place

### ✅ CORRECT: Keep root lean
**What root agent should do:**
- Route requests to correct tool/agent
- Handle simple queries (list, search)
- Delegate complex processing to sub-agents
- Keep instructions minimal and clear

### 🤔 CONSIDERATION: How to structure
```
Root Agent (lean)
├── Handles: routing, listing, querying
├── Delegates to: add_idea_agent (for processing)
└── Tools:
    ├── add_idea → calls add_idea_agent
    ├── list_ideas
    ├── query_ideas
    ├── update_idea
    ├── delete_idea
    ├── expand_idea → calls expand_idea_agent?
    └── send_weekly_report → calls report_agent?
```

### 📝 RECOMMENDATION
1. Start with MINIMAL root prompt (just routing)
2. Create robust `add_idea_agent` with all the intelligence
3. Test heavily on the 80% use case (add idea)
4. Then add other features incrementally

Sound good?
