# WhatsApp Newsletter Agent - Architecture & Setup Guide

A Google ADK-based newsletter creation system designed to work through WhatsApp, with Notion as persistent storage.

## Architecture Overview

```
WhatsApp Message
    ↓
WhatsApp Business API Webhook
    ↓
Your Backend (Vertex AI FastAPI)
    ↓
Session Manager (whatsapp_user_id → adk_session_id)
    ↓
Google ADK Newsletter Agent
    ├─ ADK State: {current_newsletter_id: "notion_page_id"}
    ├─ Sub-agents: researcher, writer, formatter
    └─ Loads/saves from Notion when needed
    ↓
Notion Database (Persistent Storage)
    └─ Your personal workspace
```

## Core Design Principles

### 1. Persistent Sessions
- Each WhatsApp user = one persistent ADK session
- Sessions never expire (unless you manually clear them)
- User can continue conversations across days/weeks

### 2. Lightweight State
- ADK state stores ONLY newsletter IDs
- Full content lives in Notion
- State example: `{"current_newsletter_id": "notion-page-abc123"}`

### 3. Database Strategy
- **Notion** = Persistent storage for newsletter content
- **ADK State** = Current context (which newsletter user is editing)
- **Your Backend** = Session mapping (whatsapp_id → session_id)

### 4. Cost Optimization
- Newsletter content loaded from Notion only when needed
- Not included in every ADK agent call
- Keeps token usage low

---

## Database Comparison: Your Own DB vs Notion

### Quick Comparison Table

| Aspect | PostgreSQL/MySQL | Notion API |
|--------|-----------------|------------|
| **Setup Complexity** | High (hosting, migrations, backups) | Low (API token + create database) |
| **Query Speed** | 10-50ms | 100-500ms |
| **Monthly Cost** | $5-20 (Supabase/PlanetScale) | $0 (free tier) |
| **Rate Limits** | None (self-hosted) or generous | 3 requests/second |
| **UI for Viewing Data** | Need to build admin panel | Beautiful built-in UI |
| **Search Capabilities** | Full-text search, complex joins | Basic filtering by properties |
| **Rich Content Support** | Need markdown parser/renderer | Native markdown + rich text |
| **Scalability** | Millions of records | Best for 1-1000 users |
| **Backup & Recovery** | Manual setup required | Automatic (Notion handles it) |
| **Data Ownership** | Full control | Depends on Notion ToS |
| **Editing Experience** | Need to build UI | Edit directly in Notion |
| **Analytics** | Full SQL queries, aggregations | Limited (must pull and process) |
| **Maintenance** | Database updates, security patches | Zero (Notion maintains) |

### Detailed Analysis

#### PostgreSQL/MySQL Pros:
- **Speed**: Sub-50ms queries, even for complex operations
- **Power**: Full SQL, indexes, transactions, joins
- **No limits**: Query as much as you want
- **Scale**: Can handle millions of newsletters
- **Analytics**: Built-in aggregations, complex reporting
- **Full control**: Your data, your rules

#### PostgreSQL/MySQL Cons:
- **Setup overhead**: Need to provision database, manage connections
- **Maintenance**: Security updates, backups, migrations
- **Cost**: $5-20/month minimum (managed hosting)
- **No UI**: Need to build admin panel to view data
- **Complexity**: Schema design, migrations, ORM setup

#### Notion Pros:
- **Zero setup**: Create database in 5 minutes
- **Free**: Personal use costs $0
- **Beautiful UI**: View/edit newsletters with rich formatting
- **Rich content**: Native markdown, embeds, images
- **No maintenance**: Notion handles everything
- **Backup included**: Notion auto-backs up your data
- **Easy debugging**: See exactly what's stored

#### Notion Cons:
- **Rate limits**: 3 requests/second (fine for 1-10 users)
- **Slower**: 100-500ms per query
- **Limited search**: Can't do complex queries like "find all newsletters mentioning 'AI' written in casual tone"
- **Vendor lock-in**: Your data lives in Notion
- **No transactions**: Can't do atomic multi-step operations
- **Analytics harder**: Need to export data to analyze

### When to Use Each

**Use Notion if:**
- ✅ Personal use or small team (1-50 users)
- ✅ Want to view/edit newsletters in a nice UI
- ✅ Don't want to manage infrastructure
- ✅ Each user generates <3 newsletters per minute
- ✅ Building MVP / prototype
- ✅ Want zero monthly costs

**Use PostgreSQL/MySQL if:**
- ✅ Planning for 100+ concurrent users
- ✅ Need complex analytics/reporting
- ✅ Require sub-50ms query response times
- ✅ Want full control over data
- ✅ Need complex search (full-text, filters, joins)
- ✅ Building production SaaS product

### For Your Use Case (Personal + WhatsApp)

**Recommendation: Start with Notion**

**Why:**
1. You're using it personally (low volume)
2. 3 req/sec = ~180 requests/minute = plenty for one person
3. You get a beautiful UI to view your newsletters
4. Zero setup and $0 cost
5. You can always migrate to PostgreSQL later if needed

**Migration Path (if you scale):**
- Export newsletters from Notion (they have export API)
- Load into PostgreSQL
- Update your backend to use SQL queries
- ADK agent code stays the same!

---

## Notion Database Setup

### Step 1: Create Notion Integration

1. Go to [https://www.notion.so/my-integrations](https://www.notion.so/my-integrations)
2. Click "New integration"
3. Name it: "Newsletter Agent"
4. Select your workspace
5. Copy the **Internal Integration Token** (starts with `secret_`)

### Step 2: Create Newsletters Database

1. Create a new page in Notion
2. Add a database (full page)
3. Name it: "Newsletters"

### Step 3: Database Schema

Add these properties to your database:

| Property Name | Type | Description |
|--------------|------|-------------|
| **Title** | Title | Newsletter topic (auto-created) |
| **Content** | Text | Full newsletter markdown content |
| **Tone** | Select | Options: Professional, Casual, Friendly, Authoritative |
| **Audience** | Text | Target audience description |
| **Status** | Select | Options: Draft, Completed, Published, Archived |
| **Created** | Created time | Auto-populated |
| **Last Edited** | Last edited time | Auto-populated |
| **Version** | Number | Track edit versions |
| **User ID** | Text | WhatsApp user identifier (for multi-user future) |

### Step 4: Share Database with Integration

1. Click "..." on your database
2. Click "Connections" → "Connect to"
3. Select "Newsletter Agent" integration
4. Database is now accessible via API

### Step 5: Get Database ID

The database ID is in the URL:
```
https://notion.so/{workspace}/DATABASE_ID?v=...
                              ^^^^^^^^^^^^
                              This is your database ID
```

Example: `https://notion.so/myworkspace/a1b2c3d4e5f6...`
Database ID = `a1b2c3d4e5f6...`

---

## System Architecture Details

### Session Management

```python
# Session mapping stored in your backend (lightweight storage)
{
    "whatsapp:+1234567890": {
        "adk_session_id": "session_abc123",
        "created_at": "2025-10-12T10:00:00Z",
        "last_active": "2025-10-12T15:30:00Z"
    }
}
```

### ADK State Management

```python
# ADK session state (minimal, just IDs)
{
    "current_newsletter_id": "notion-page-xyz789",
    "mode": "editing",  # or "creating", "idle"
    "last_interaction": "2025-10-12T15:30:00Z"
}
```

### Notion Storage

```python
# Full newsletter stored in Notion
{
    "page_id": "notion-page-xyz789",
    "properties": {
        "Title": "AI Trends for Developers",
        "Content": "[Full 500-word newsletter...]",
        "Tone": "Casual",
        "Audience": "Software developers",
        "Status": "Completed",
        "Version": 3
    }
}
```

### Data Flow Examples

#### Creating New Newsletter

```
1. User (WhatsApp): "Create newsletter about AI for developers, casual tone"

2. Backend:
   - Receives webhook from WhatsApp
   - Gets/creates ADK session for user

3. ADK Agent:
   - Parses: topic="AI", audience="developers", tone="casual"
   - Calls researcher sub-agent → gathers insights
   - Calls writer sub-agent → creates content
   - Calls formatter sub-agent → formats newsletter
   - Returns complete newsletter

4. Backend:
   - Saves newsletter to Notion via API
   - Updates ADK state: {"current_newsletter_id": "notion-page-123"}
   - Sends newsletter back to WhatsApp
```

**Cost:** ~1000 tokens (full research + write + format)
**Notion API calls:** 1 (save newsletter)

#### Editing Existing Newsletter

```
1. User (WhatsApp): "Make it more professional"

2. Backend:
   - Gets ADK session
   - Checks state → current_newsletter_id = "notion-page-123"

3. ADK Agent:
   - Knows which newsletter to edit (from state)
   - Loads newsletter from Notion
   - Makes edits (adjusts tone to professional)
   - Returns edited version

4. Backend:
   - Updates newsletter in Notion
   - Increments version number
   - Sends edited newsletter to WhatsApp
```

**Cost:** ~300-500 tokens (edit only, no research)
**Notion API calls:** 2 (load + update)

#### Editing Old Newsletter

```
1. User (WhatsApp): "Edit the blockchain newsletter from last week"

2. Backend:
   - Gets ADK session
   - Agent needs to find the newsletter

3. ADK Agent:
   - Searches Notion: "blockchain" + created_time filter
   - Finds newsletter: notion-page-456
   - Updates state: {"current_newsletter_id": "notion-page-456"}
   - Loads content from Notion
   - Waits for user's edit instruction

4. User (WhatsApp): "Add a section about NFTs"

5. ADK Agent:
   - Knows current newsletter (from state)
   - Makes edit
   - Saves to Notion
```

**Cost:** ~500 tokens (search + load + edit)
**Notion API calls:** 3 (search + load + update)

---

## Deployment on Vertex AI

### Overview

Vertex AI automatically wraps your Google ADK agent as a FastAPI endpoint, handling:
- API routing
- Request/response formatting
- Scaling
- Authentication

### Deployment Steps

1. **Ensure your agent exports `root_agent`:**
```python
# In agent.py or whatsapp_agent.py
root_agent = whatsapp_newsletter_agent
```

2. **Install Google ADK:**
```bash
pip install google-adk
```

3. **Deploy to Vertex AI:**
```bash
# From your project directory
google-adk deploy newsletter_agent \
    --project-id YOUR_GCP_PROJECT \
    --region us-central1 \
    --env-file .env
```

4. **Vertex AI will:**
   - Create FastAPI wrapper automatically
   - Deploy as Cloud Run service
   - Provide endpoint URL: `https://xxx.run.app`

### Environment Variables

Create `.env` file:
```bash
# Notion Configuration
NOTION_API_TOKEN=secret_xxxxxxxxxxxxxxx
NOTION_DATABASE_ID=a1b2c3d4e5f6...

# WhatsApp Configuration (optional for local testing)
WHATSAPP_API_TOKEN=your_whatsapp_token
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id

# Google Cloud
GOOGLE_CLOUD_PROJECT=your-gcp-project
```

### Vertex AI Endpoint Structure

Once deployed, Vertex AI creates these endpoints:

```
POST /sessions                          # Create new session
POST /sessions/{session_id}/messages    # Send message to session
GET  /sessions/{session_id}             # Get session info
DELETE /sessions/{session_id}           # Delete session
```

### Your Webhook Integration

```python
# Your webhook server (separate from Vertex AI)
from flask import Flask, request
import requests

app = Flask(__name__)

VERTEX_AI_ENDPOINT = "https://your-agent.run.app"
SESSION_STORE = {}  # Map whatsapp_id → session_id

@app.route('/whatsapp/webhook', methods=['POST'])
def whatsapp_webhook():
    data = request.json
    whatsapp_user_id = data['from']
    message = data['message']['text']

    # Get or create session
    if whatsapp_user_id not in SESSION_STORE:
        # Create new session in Vertex AI
        response = requests.post(f"{VERTEX_AI_ENDPOINT}/sessions")
        SESSION_STORE[whatsapp_user_id] = response.json()["session_id"]

    session_id = SESSION_STORE[whatsapp_user_id]

    # Send message to ADK agent via Vertex AI
    response = requests.post(
        f"{VERTEX_AI_ENDPOINT}/sessions/{session_id}/messages",
        json={"message": message}
    )

    agent_response = response.json()["response"]

    # Send response back to WhatsApp
    send_whatsapp_message(whatsapp_user_id, agent_response)

    return {"status": "ok"}
```

---

## Cost Analysis (Personal Use)

### Google ADK / Gemini Costs

**Model:** `gemini-2.5-flash`

**Pricing (as of 2025):**
- Input: $0.075 per 1M tokens
- Output: $0.30 per 1M tokens

**Typical Newsletter Creation:**
- Research: ~500 input + 300 output = 800 tokens
- Writing: ~800 input + 600 output = 1,400 tokens
- Formatting: ~700 input + 100 output = 800 tokens
- **Total: ~3,000 tokens per newsletter**

**Cost per newsletter:** ~$0.0005 (half a cent)

**Monthly personal use (20 newsletters):**
- 20 newsletters × 3,000 tokens = 60,000 tokens
- **Cost: ~$0.01/month** (basically free)

### Notion API Costs

**Free tier:**
- Unlimited pages/blocks for personal workspace
- 3 requests/second rate limit
- **Cost: $0**

### Vertex AI / Cloud Run Costs

**Cloud Run pricing:**
- Free tier: 2 million requests/month
- CPU: $0.00002400/vCPU-second
- Memory: $0.00000250/GiB-second

**Personal use estimate:**
- 20 newsletters/month × 30 seconds each = 600 seconds
- CPU: 600s × $0.000024 = **$0.014/month**
- Memory: 600s × 0.5GB × $0.0000025 = **$0.001/month**
- **Total: ~$0.015/month** (essentially free)

### Total Monthly Cost (Personal Use)

```
Gemini API:        $0.01
Notion API:        $0.00
Vertex AI:         $0.015
WhatsApp (Meta):   $0.00 (1000 free messages/month)
-------------------------
TOTAL:            ~$0.025/month (2.5 cents)
```

**For 100 newsletters/month:** ~$0.10/month (10 cents)

### When Costs Increase

**Multi-user scenario (100 users, 10 newsletters each = 1000 newsletters/month):**
- Gemini: ~$1.50/month
- Vertex AI: ~$5/month
- Notion: Still $0 (rate limits may be issue)
- **Total: ~$6.50/month**

---

## File Structure

```
newsletter_agent/
├── agent.py                      # Original multi-session coordinator
├── whatsapp_agent.py             # WhatsApp-optimized agent
├── prompt.py                     # Agent prompts
├── notion_client.py              # Notion API wrapper
├── session_manager.py            # Session/state management
├── webhook_server.py             # WhatsApp webhook handler
├── requirements.txt              # Dependencies
├── .env                          # Configuration
├── README.md                     # Original README
└── WHATSAPP_SETUP.md            # This file

sub_agents/
├── researcher/
│   ├── agent.py
│   └── prompt.py
├── writer/
│   ├── agent.py
│   └── prompt.py
└── formatter/
    ├── agent.py
    └── prompt.py
```

---

## Dependencies

```txt
# requirements.txt
google-adk>=0.1.0
notion-client>=2.0.0
flask>=3.0.0
requests>=2.31.0
python-dotenv>=1.0.0
```

Install:
```bash
pip install -r requirements.txt
```

---

## Usage Examples

### Example 1: Create Newsletter

**User sends via WhatsApp:**
```
Create a newsletter about AI productivity tools for software engineers, keep it casual
```

**Agent response:**
```
📰 Your Newsletter is Ready!

# AI Tools That Actually Save You Time (Not Just Hype)

Let's be real—most "AI productivity tools" are just ChatGPT with a fancy wrapper. But here are three that actually changed how I work:

## 1. GitHub Copilot (The OG)
Still the king. But here's the trick: use it for boilerplate, not logic...

[Full newsletter content]

---
Created for: Software engineers
Tone: Casual
Topic: AI productivity tools
Stored in Notion ✓
```

### Example 2: Edit Current Newsletter

**User sends:**
```
Make the intro more punchy
```

**Agent response:**
```
✏️ Updated Newsletter

# Stop Wasting Time—These 3 AI Tools Actually Work

Most AI tools are vaporware. These three aren't.

[Rest of newsletter...]

Version 2 saved to Notion ✓
```

### Example 3: Edit Old Newsletter

**User sends:**
```
Edit the crypto newsletter from last week
```

**Agent response:**
```
📂 Found: "Crypto Trends for Investors" (created Oct 5)
Now editing this newsletter. What would you like to change?
```

**User sends:**
```
Add a section about Bitcoin ETFs
```

**Agent response:**
```
✏️ Updated Newsletter

[Original content...]

## Bitcoin ETFs: The Game Changer

[New section added...]

Version 3 saved to Notion ✓
```

---

## Troubleshooting

### Issue: Notion API returns 401 Unauthorized

**Solution:**
1. Check your `NOTION_API_TOKEN` in `.env`
2. Ensure integration is connected to the database
3. Verify token hasn't been regenerated

### Issue: Session not persisting

**Solution:**
1. Check session storage (Redis/file/memory)
2. Verify `whatsapp_user_id` is consistent
3. Check Vertex AI session hasn't expired

### Issue: Slow responses (>30 seconds)

**Solution:**
1. This is normal for newsletter creation (research takes time)
2. Send immediate acknowledgment to user
3. Process async and send newsletter when done

### Issue: Rate limit errors from Notion

**Solution:**
1. Personal use shouldn't hit this (3 req/sec)
2. Add caching for frequently accessed newsletters
3. Batch operations if possible

### Issue: Newsletter content truncated

**Solution:**
1. Notion blocks have size limits
2. Split long newsletters into multiple blocks
3. Use proper Notion API pagination

---

## Limitations

### Current Limitations

1. **Single user:** Currently configured for personal use
2. **No OAuth:** Uses your Notion token (not user's)
3. **No authentication:** WhatsApp webhook should validate requests
4. **No rate limiting:** Could be abused if endpoint is public
5. **No analytics:** No tracking of newsletter performance

### Future Improvements

1. **Multi-user OAuth:** Let users connect their Notion
2. **Newsletter templates:** Pre-built structures
3. **Scheduling:** Create and schedule newsletters
4. **Analytics:** Track views, clicks in Notion
5. **Version comparison:** Diff between newsletter versions
6. **Export options:** PDF, HTML email, Medium post

---

## Migration Path to PostgreSQL

If you outgrow Notion:

### Step 1: Export Data
```python
# Export all newsletters from Notion
newsletters = notion.databases.query(database_id=DB_ID)
```

### Step 2: Create PostgreSQL Schema
```sql
CREATE TABLE newsletters (
    id UUID PRIMARY KEY,
    user_id TEXT NOT NULL,
    topic TEXT NOT NULL,
    content TEXT NOT NULL,
    tone TEXT,
    audience TEXT,
    status TEXT,
    version INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Step 3: Migrate Data
```python
for page in newsletters:
    db.execute("""
        INSERT INTO newsletters (id, topic, content, ...)
        VALUES (?, ?, ?, ...)
    """, extract_notion_data(page))
```

### Step 4: Update Backend
```python
# Change from Notion client to PostgreSQL
# from notion_client import Client
from psycopg2 import connect

# Update CRUD operations
def get_newsletter(newsletter_id):
    return db.query("SELECT * FROM newsletters WHERE id = ?", newsletter_id)
```

**Agent code stays the same!** Only backend storage changes.

---

## Security Considerations

### For Personal Use

1. **Notion token:** Keep secret, never commit to git
2. **WhatsApp webhook:** Validate incoming requests
3. **Vertex AI endpoint:** Use authentication (API keys)

### For Multi-User (Future)

1. **OAuth:** Let users connect their Notion
2. **Token storage:** Encrypt user tokens in database
3. **Rate limiting:** Prevent abuse
4. **Input validation:** Sanitize user messages
5. **GDPR compliance:** User data in their Notion = compliant

---

## Support & Resources

### Documentation

- [Google ADK Docs](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-builder)
- [Notion API Docs](https://developers.notion.com/)
- [WhatsApp Business API](https://developers.facebook.com/docs/whatsapp)

### Common Questions

**Q: Can I use this for multiple users?**
A: Yes, but you'll need OAuth so each user connects their Notion.

**Q: What if Notion is down?**
A: Add fallback storage (PostgreSQL) or queue operations.

**Q: How do I backup newsletters?**
A: Notion handles backups, but you can export periodically.

**Q: Can I use Google Sheets instead of Notion?**
A: Yes! Replace `notion_client.py` with Google Sheets API.

---

## License

Same as parent project.
