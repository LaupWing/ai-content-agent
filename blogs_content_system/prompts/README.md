# Blog Writer Prompts System

This directory contains all prompt versions for the blog writer agent, with versioning and testing capabilities.

## Directory Structure

```
prompts/
├── README.md (this file)
├── modes/
│   ├── quick_mode.py          # Fast, direct blog generation
│   └── thoughtout_mode.py     # Interactive, step-by-step with user input
├── archive/
│   ├── v1_quick_[date].py     # Historical quick mode versions
│   └── v1_thoughtout_[date].py # Historical thoughtout mode versions
└── testing/
    ├── test_prompts.py        # Framework for testing prompts
    ├── test_cases.json        # Test topics and expected outputs
    └── results/               # Test results for comparison
```

## Two Modes Explained

### Quick Mode
**Use when:** User wants fast results, trusts the AI, minimal back-and-forth

**Behavior:**
- Takes topic input
- Immediately generates complete 1500-2500 word blog
- Picks best headline automatically
- No intermediate questions
- One-shot generation

**Example:**
```
User: "Write about productivity for remote workers"
AI: [Generates complete blog immediately]
```

### Thought-out Mode
**Use when:** User wants control, wants to refine direction, prefers collaboration

**Behavior:**
- Shows 5 headline options with angles
- Asks for optional context/preferences
- Generates blog based on chosen direction
- Offers adjustments after generation
- Iterative refinement

**Example:**
```
User: "Write about productivity for remote workers"
AI: "Here are 5 directions we could take this..."
User: "I like option 2"
AI: "Want to add any context? Or should I go?"
User: "Add that I work from coffee shops"
AI: [Generates blog with that context]
```

## Usage in Code

```python
from prompts.modes import quick_mode, thoughtout_mode

# Quick mode
agent = Agent(
    name="blog_writer_quick",
    instruction=quick_mode.PROMPT,
    ...
)

# Thoughtout mode
agent = Agent(
    name="blog_writer_thoughtout",
    instruction=thoughtout_mode.PROMPT,
    ...
)
```

## Version Management

When you update a prompt:

1. Copy current version to `archive/` with date: `v1_quick_20251011.py`
2. Update the prompt in `modes/`
3. Run tests to compare: `python testing/test_prompts.py --compare v1 v2`
4. Document changes in the version file

## Testing Prompts

```bash
# Test current quick mode
python testing/test_prompts.py --mode quick

# Test current thoughtout mode
python testing/test_prompts.py --mode thoughtout

# Compare two versions
python testing/test_prompts.py --compare quick_v1 quick_v2

# Test on specific topic
python testing/test_prompts.py --mode quick --topic "productivity"
```

## Prompt Quality Checklist

Before finalizing a prompt version:

- [ ] Length: Under 200 lines for quick, under 300 for thoughtout
- [ ] Clarity: Instructions are unambiguous
- [ ] Tested: Ran on at least 5 test topics
- [ ] Compared: Better than previous version
- [ ] Documented: Changes noted in archive file
- [ ] No contradictions: Instructions don't conflict
- [ ] Appropriate complexity: Not over-constraining the model
