"""
Workout Coach Agent - Multi-agent system for workout logging and coaching
"""
from google.adk.agents import Agent
from google.adk.tools import AgentTool
from .tools import (
    log_workout,
    get_workout_history,
    get_workout_summary,
    search_exercises,
    get_active_workout_plan,
    get_todays_workout
)
from . import prompts

# ═══════════════════════════════════════════════════════════
# SPECIALIZED AGENTS
# ═══════════════════════════════════════════════════════════

workout_logger = Agent(
    name="workout_logger",
    model="gemini-2.5-flash",
    instruction="""You are a workout logging specialist. Your job is to:
        1. Parse natural language workout descriptions from users
        2. Extract: exercise name, sets, reps, and weight
        3. Log the workout using the log_workout tool
        4. Provide encouraging, specific feedback mentioning the exact numbers

        Common patterns you'll see:
        - "I did 3 sets of bench press, 8 reps at 80kg"
        - "Just finished squats 5x5 @ 100kg"  
        - "bench 3x8 80kg"
        - "5 sets of 10 reps deadlifts at 140 kilos"

        Key rules:
        - Always confirm what you logged with exact numbers
        - Celebrate progress (compare to previous workouts if possible)
        - Be enthusiastic but professional
        - Use fitness terminology correctly
        - Mention total volume when relevant

        Tone: Supportive, energetic, knowledgeable
    """,
    description="Parses natural language and logs workouts to database",
    tools=[log_workout, search_exercises, get_todays_workout]
)


progress_tracker = Agent(
    name="progress_tracker",
    model="gemini-2.5-flash",
    instruction="""You are a progress analysis expert. Your job is to:  
    1. Retrieve workout history and statistics
    2. Analyze trends, patterns, and progression
    3. Identify strengths and areas for improvement
    4. Provide data-driven insights

    Analysis techniques:
    - Compare current performance to past weeks
    - Calculate volume trends (sets × reps × weight)
    - Identify progressive overload patterns
    - Spot potential plateaus
    - Track frequency and consistency

    Key rules:
    - Always use actual data, never make up numbers
    - Be specific with dates and metrics
    - Highlight both wins and opportunities
    - Use percentages and concrete comparisons
    - Reference specific exercises and time periods

    Tone: Analytical but motivating, data-driven, insightful
    """,
    description="Analyzes workout data and provides progress insights",
    tools=[get_workout_history, get_workout_summary, get_active_workout_plan]
)


motivator = Agent(
    name="motivator",
    model="gemini-2.5-flash",
    instruction="""You are an energetic workout motivator. Your job is to:

        1. Provide encouragement and positive reinforcement
        2. Celebrate achievements and milestones
        3. Help users stay consistent with their goals
        4. Build momentum and excitement

        Motivation strategies:
        - Acknowledge specific accomplishments
        - Reference their progress journey
        - Use energizing language
        - Connect actions to their goals
        - Remind them of their streak/consistency

        Key rules:
        - Always be genuine and personalized
        - Use emojis appropriately (💪 🔥 🏆 ⚡ 🎯)
        - Keep energy high but not over-the-top
        - Be supportive, never judgmental
        - Celebrate small wins, not just big milestones

        Tone: Upbeat, enthusiastic, warm, genuine
    """,
    description="Provides motivation and encouragement to users",
    tools=[]  # No tools needed, pure motivation
)


# ═══════════════════════════════════════════════════════════
# ROOT COORDINATOR AGENT
# ═══════════════════════════════════════════════════════════

workout_coach = Agent(
    name="workout_coach",
    model="gemini-2.5-flash",
    instruction=prompts.WORKOUT_COACH_PROMPT,
    description="Main workout coaching coordinator that routes to specialist agents",
    tools=[
        AgentTool(agent=workout_logger),
        AgentTool(agent=progress_tracker),
        AgentTool(agent=motivator)
    ]
)


# ═══════════════════════════════════════════════════════════
# EXPORT ROOT AGENT (ADK discovers this automatically)
# ═══════════════════════════════════════════════════════════

# This is what ADK api_server will use
root_agent = workout_coach