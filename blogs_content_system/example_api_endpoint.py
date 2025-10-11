"""
Example API Endpoint for Laravel Integration

This shows how your Laravel backend would call the Python service
with the mode toggle.

In your actual Laravel app, this would be a service that communicates
with this Python API via HTTP.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from enum import Enum
from agent_with_modes import create_blog_writer

app = FastAPI()


class BlogMode(str, Enum):
    QUICK = "quick"
    THOUGHTOUT = "thoughtout"


class BlogRequest(BaseModel):
    """Request model for blog generation"""
    topic: str
    mode: BlogMode = BlogMode.QUICK
    user_id: int
    additional_context: str | None = None
    headline_choice: int | None = None  # For thoughtout mode step 2


class BlogResponse(BaseModel):
    """Response model for blog generation"""
    content: str
    mode: str
    status: str
    needs_input: bool = False  # True if waiting for user input (thoughtout mode)
    session_id: str | None = None


@app.post("/generate-blog", response_model=BlogResponse)
async def generate_blog(request: BlogRequest):
    """
    Generate a blog based on mode

    Quick mode: Returns complete blog immediately
    Thoughtout mode: Returns headline options, then generates after user chooses
    """
    try:
        # Create agent with specified mode
        agent = create_blog_writer(mode=request.mode.value)

        # For quick mode, just generate immediately
        if request.mode == BlogMode.QUICK:
            response = agent.send_message(request.topic)

            return BlogResponse(
                content=response.content,
                mode="quick",
                status="complete",
                needs_input=False
            )

        # For thoughtout mode, handle conversation flow
        elif request.mode == BlogMode.THOUGHTOUT:
            # If this is the first request (no headline choice yet)
            if request.headline_choice is None:
                response = agent.send_message(request.topic)

                return BlogResponse(
                    content=response.content,  # This will be the headline options
                    mode="thoughtout",
                    status="awaiting_headline_choice",
                    needs_input=True,
                    session_id="session_123"  # In reality, store agent session
                )

            # If user has chosen a headline
            else:
                # Continue conversation with agent
                # (You'd need to restore the agent session here)
                choice_message = f"I choose option {request.headline_choice}"

                if request.additional_context:
                    choice_message += f". Additional context: {request.additional_context}"
                else:
                    choice_message += ". Go!"

                response = agent.send_message(choice_message)

                return BlogResponse(
                    content=response.content,  # This will be the complete blog
                    mode="thoughtout",
                    status="complete",
                    needs_input=False
                )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/modes")
async def get_modes():
    """Return available modes and their descriptions"""
    return {
        "modes": [
            {
                "id": "quick",
                "name": "Quick Mode",
                "description": "Fast, one-shot blog generation. AI makes all decisions.",
                "use_when": "You want fast results and trust the AI to pick the best approach",
                "steps": 1,
                "estimated_time": "30-60 seconds"
            },
            {
                "id": "thoughtout",
                "name": "Thought-out Mode",
                "description": "Interactive, step-by-step with your input. You control the direction.",
                "use_when": "You want to guide the direction and refine the approach",
                "steps": 3,
                "estimated_time": "2-5 minutes (with your input)"
            }
        ]
    }


# Example Laravel Controller Integration:
"""
<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;

class BlogGenerationController extends Controller
{
    private $pythonServiceUrl = 'http://localhost:8000';

    public function generateBlog(Request $request)
    {
        $validated = $request->validate([
            'topic' => 'required|string',
            'mode' => 'required|in:quick,thoughtout',
            'headline_choice' => 'nullable|integer|min:1|max:5',
            'additional_context' => 'nullable|string',
        ]);

        // Call Python service
        $response = Http::post("{$this->pythonServiceUrl}/generate-blog", [
            'topic' => $validated['topic'],
            'mode' => $validated['mode'],
            'user_id' => auth()->id(),
            'headline_choice' => $validated['headline_choice'] ?? null,
            'additional_context' => $validated['additional_context'] ?? null,
        ]);

        if ($response->successful()) {
            $data = $response->json();

            // If needs user input (thoughtout mode, step 1)
            if ($data['needs_input']) {
                return response()->json([
                    'status' => 'awaiting_input',
                    'headline_options' => $data['content'],
                    'session_id' => $data['session_id'],
                ]);
            }

            // Blog is complete
            return response()->json([
                'status' => 'complete',
                'blog' => $data['content'],
                'mode' => $data['mode'],
            ]);
        }

        return response()->json(['error' => 'Generation failed'], 500);
    }

    public function getModes()
    {
        $response = Http::get("{$this->pythonServiceUrl}/modes");

        if ($response->successful()) {
            return response()->json($response->json());
        }

        return response()->json(['error' => 'Could not fetch modes'], 500);
    }
}
"""

# Example Vue.js Frontend Component:
"""
<template>
  <div class="blog-generator">
    <!-- Mode Toggle -->
    <div class="mode-selector">
      <button
        v-for="mode in modes"
        :key="mode.id"
        @click="selectedMode = mode.id"
        :class="{ active: selectedMode === mode.id }"
      >
        <h3>{{ mode.name }}</h3>
        <p>{{ mode.description }}</p>
        <span class="time">{{ mode.estimated_time }}</span>
      </button>
    </div>

    <!-- Input Section -->
    <div v-if="step === 'input'" class="input-section">
      <textarea
        v-model="topic"
        placeholder="What do you want to write about?"
      ></textarea>
      <button @click="generateBlog">Generate Blog</button>
    </div>

    <!-- Headline Selection (Thoughtout Mode Only) -->
    <div v-if="step === 'headlines'" class="headline-section">
      <h2>Choose a direction:</h2>
      <div v-html="headlineOptions"></div>
      <input
        v-model="headlineChoice"
        type="number"
        min="1"
        max="5"
        placeholder="Enter 1-5"
      />
      <textarea
        v-model="additionalContext"
        placeholder="Optional: Add any context or preferences"
      ></textarea>
      <button @click="submitHeadlineChoice">Continue</button>
    </div>

    <!-- Result -->
    <div v-if="step === 'complete'" class="result-section">
      <div class="blog-content" v-html="blogContent"></div>
      <button @click="reset">Generate Another</button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="loading">
      Generating your blog...
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      modes: [],
      selectedMode: 'quick',
      topic: '',
      step: 'input',
      loading: false,
      headlineOptions: '',
      headlineChoice: null,
      additionalContext: '',
      blogContent: '',
      sessionId: null,
    }
  },
  mounted() {
    this.fetchModes()
  },
  methods: {
    async fetchModes() {
      const response = await fetch('/api/blog/modes')
      this.modes = await response.json().modes
    },
    async generateBlog() {
      this.loading = true
      const response = await fetch('/api/blog/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          topic: this.topic,
          mode: this.selectedMode,
        }),
      })

      const data = await response.json()
      this.loading = false

      if (data.status === 'awaiting_input') {
        // Thoughtout mode: show headline options
        this.step = 'headlines'
        this.headlineOptions = data.headline_options
        this.sessionId = data.session_id
      } else if (data.status === 'complete') {
        // Quick mode or final result
        this.step = 'complete'
        this.blogContent = data.blog
      }
    },
    async submitHeadlineChoice() {
      this.loading = true
      const response = await fetch('/api/blog/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          topic: this.topic,
          mode: this.selectedMode,
          headline_choice: this.headlineChoice,
          additional_context: this.additionalContext,
        }),
      })

      const data = await response.json()
      this.loading = false

      if (data.status === 'complete') {
        this.step = 'complete'
        this.blogContent = data.blog
      }
    },
    reset() {
      this.step = 'input'
      this.topic = ''
      this.headlineChoice = null
      this.additionalContext = ''
      this.blogContent = ''
    },
  },
}
</script>

<style scoped>
.mode-selector {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-bottom: 2rem;
}

.mode-selector button {
  padding: 1.5rem;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.mode-selector button.active {
  border-color: #3b82f6;
  background-color: #eff6ff;
}

.mode-selector button:hover {
  border-color: #93c5fd;
}

.time {
  display: block;
  font-size: 0.875rem;
  color: #6b7280;
  margin-top: 0.5rem;
}
</style>
"""

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
