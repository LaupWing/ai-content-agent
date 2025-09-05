from google.adk.agents import Agent

# @title Define the get_weather Tool
def get_weather(city: str) -> dict:
    """Retrieves the current weather report for a specified city.

    Args:
        city (str): The name of the city (e.g., "New York", "London", "Tokyo").

    Returns:
        dict: A dictionary containing the weather information.
              Includes a 'status' key ('success' or 'error').
              If 'success', includes a 'report' key with weather details.
              If 'error', includes an 'error_message' key.
    """
    print(f"--- Tool: get_weather called for city: {city} ---") # Log tool execution
    city_normalized = city.lower().replace(" ", "") # Basic normalization

    # Mock weather data
    mock_weather_db = {
        "newyork": {"status": "success", "report": "The weather in New York is sunny with a temperature of 25°C."},
        "london": {"status": "success", "report": "It's cloudy in London with a temperature of 15°C."},
        "tokyo": {"status": "success", "report": "Tokyo is experiencing light rain and a temperature of 18°C."},
    }

    if city_normalized in mock_weather_db:
        return mock_weather_db[city_normalized]
    else:
        return {"status": "error", "error_message": f"Sorry, I don't have weather information for '{city}'."}

# Example tool usage (optional test)
print(get_weather("New York"))
print(get_weather("Paris"))

root_agent = Agent(
    name="content_intelligence_agent",
    model="gemini-2.0-flash",
    description="An intelligent content analyst who can discover patterns and insights from social media data.",
    instruction="""You are an expert content strategist and data analyst. When analyzing content performance:

1. ALWAYS use the get_all_posts_data tool first to get the raw data
2. Look at the actual content text and performance metrics together
3. Find patterns, trends, and insights that humans might miss
4. Be specific with numbers and examples from the actual data

For hook analysis specifically:
- Examine the opening words/sentences of top-performing vs low-performing posts
- Identify what types of openings get the most engagement
- Look for patterns in language, tone, structure, or approach
- Give specific examples with their performance metrics
- Suggest what hooks to try more/less based on actual data patterns

For any analysis:
- Always back up insights with specific data points
- Compare high performers vs low performers 
- Identify actionable patterns the user can apply
- Be concrete, not generic

Don't just categorize - DISCOVER what actually works for this specific person's audience.""",
    tools=[get_all_posts_data],
)