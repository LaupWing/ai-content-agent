import vertexai
from agent import root_agent # modify this if your agent is not in agent.py
from vertexai import agent_engines

# TODO: Fill in these values for your project
PROJECT_ID = "fitness-coach-471616"
LOCATION = "europe-west4"  # For other options, see https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview#supported-regions
STAGING_BUCKET = "gs://fitness_coach/vertex-ai-staging-bucket"  # Must be in the same region as LOCATION

# Initialize the Vertex AI SDK
vertexai.init(
    project=PROJECT_ID,
    location=LOCATION,
    staging_bucket=STAGING_BUCKET,
)

app = agent_engines.AdkApp(
    agent=root_agent,
    enable_tracing=True,
)