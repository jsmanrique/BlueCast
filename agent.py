import json
from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import AgentTool
from google.genai import types

# =============================================================================
# Configuration
# =============================================================================

APP_NAME = "surf_forecast_app"
USER_ID = "surfer_user"
SESSION_ID = "surf_session_1"
MODEL = "gemini-2.5-flash-lite"

retry_config = types.HttpRetryOptions(
    attempts=5,  # Maximum retry attempts
    exp_base=7,  # Delay multiplier
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],  # Retry on these HTTP errors
)

# =============================================================================
# Tools
# =============================================================================

def get_coordinates_tool(location: str) -> str:
    import requests

    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {"name": location, "count": 1, "language": "es", "format": "json"}

    response = requests.get(url, params=params)
    data = response.json()

    if "results" in data and len(data["results"]) > 0:
        result = data["results"][0]
        lat = result['latitude']
        lon = result['longitude']
        nombre = result['name']
        return f"latitud: {lat}, longitud: {lon}, lugar: {nombre}"
    else:
        return "No se encontraron coordenadas para este lugar"

def get_marine_forecast_tool(latitude: float, longitude: float) -> str:
    import requests
    from datetime import datetime, timedelta

    url = "https://marine-api.open-meteo.com/v1/marine"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": "wave_height,wave_direction,wave_period",
        "forecast_days": 3,
    }

    response = requests.get(url, params=params)
    data = response.json()

    return json.dumps(data, indent=2)

# =============================================================================
# AGENT 1: GeocodingAgent - Get location coordinates
# =============================================================================
geocoding_agent = LlmAgent(
    name="GeocodingAgent",
    model=MODEL,
    #code_executor=BuiltInCodeExecutor(),
    tools = [get_coordinates_tool],
    instruction="""You are an agent specialized in obtaining geographic coordinates.

MANDATORY PROCESS:
1. Identify the name of the place in the user's query
2. Execute the tool to get the coordinates of the place
3. Return the coordinates in the specified format 
CORRECT RESPONSE EXAMPLE:
latitude: 43.3183, longitude: -1.9812, place: San Sebastián

IMPORTANT: Your answer MUST contain exactly that format with the numbers and the place name.""",
    output_key="coordinates",
    description="Get geographical coordinates using Geocoding API from Open Meteo.",
)

# =============================================================================
# AGENT 2: MarineForecastAgent
# =============================================================================
marine_forecast_agent = LlmAgent(
    name="MarineForecastAgent",
    model=MODEL,
    tools=[get_marine_forecast_tool],
    instruction="""You are an agent specialized in obtaining marine weather forecasts.
    MANDATORY PROCESS:
    1. Extract latitude and longitude from the user's query.
    2. Execute the tool to get the marine weather forecast.
    3. Return the marine weather forecast in JSON format.""",
    output_key="marine_forecast",
    description="Get marine weather forecast using Marine API from Open Meteo.",
)

# =============================================================================
# AGENT 3: SurfCoach - Provide surf advice based on forecast
# =============================================================================
surf_coach_agent = LlmAgent(
    name="SurfCoachAgent",
    model=MODEL,
    instruction="""You are a surf coach agent that provides surf advice based on marine weather forecasts.
    MANDATORY PROCESS:
    1. Analyze the marine weather forecast provided in JSON format.
    2. Provide surf advice based on wave height, wave period, and wave direction.
    3. Once you have both responses, interpret the wave conditions considering:

    * **Wave height:**

    * 0.3–0.8m: Small waves, ideal for beginners
    * 0.8–1.5m: Medium waves, good for intermediate surfers
    * 1.5–2.5m: Large waves, for advanced surfers
    * > 2.5m: Very large waves, for experts only

    * **Wave period:**

    * <6s: Short period, choppy and irregular waves
    * 6–10s: Medium period, good conditions
    * 10–14s: Long period, excellent conditions (quality swell)
    * > 14s: Very long period, powerful and consistent waves

    * **Wave direction (in degrees):**

    * 0°/360° = North
    * 90° = East
    * 180° = South
    * 270° = West

    Provide your final answer including:

    1. Use same language as the user
    2. A friendly greeting mentioning the full location
    3. The forecast dates and times
    4. A clear explanation of the wave conditions and their evolution over the day
    5. A recommendation about whether it’s a good day to surf and for what level
    6. A motivating comment

    Use a **warm and enthusiastic tone**, like a surfer friend giving advice.
    """,
    output_key="surf_advice",
    description="Provide surf advice based on marine weather forecast.",
)

# =============================================================================
# Agents pipeline
# =============================================================================
agents_pipeline = SequentialAgent(
    name="AgentsPipeline",
    sub_agents=[geocoding_agent, marine_forecast_agent, surf_coach_agent],
    description="Pipeline to get surf advice based on user location.",
)

# =============================================================================
# Root agent
# =============================================================================
root_agent = agents_pipeline

# =============================================================================
# Runner
# =============================================================================
session_service = InMemorySessionService()

runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_service)