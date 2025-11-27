#!/usr/bin/env python

# SPDX-FileCopyrightText: © 2025 J. Manrique Lopez de la Fuente <jsmanrique@gmail.com>
# SPDX-License-Identifier: MIT

"""
agent.py: Agentic architecture for Surf Forecast Application
"""

__author__      = "J. Manrique Lopez de la Fuente"
__copyright__   = "2025. J. Manrique Lopez de la Fuente"
__license__     = "MIT"

from google.adk.agents import Agent, LlmAgent, SequentialAgent, LoopAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import FunctionTool
from google.adk.tools.tool_context import ToolContext
from google.genai import types

from geopy.geocoders import Nominatim

import sys
import logging
import requests
import uuid
import asyncio
from dotenv import load_dotenv

# =============================================================================
# Configuration
# =============================================================================

logging.basicConfig(level=logging.INFO, stream = sys.stdout,
                    format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')
logger = logging.getLogger(__name__)

APP_NAME = "surf_forecast_app"
MODEL = "gemini-2.5-flash-lite"

# =============================================================================
# Tools
# =============================================================================

def check_preferences_complete(tool_context: ToolContext) -> dict:

    state = tool_context.state

    required = {
        'wave_height': state.get('user:wave_height'),
        'experience_level': state.get('user:experience_level')
    }

    missing = [key for key, value in required.items() if value is None]
    
    return {
        'complete': len(missing) == 0,
        'missing': missing,
        'collected': {k: v for k, v in required.items() if v is not None}
    }

def save_wave_height(height: str, tool_context: ToolContext) -> dict:
    state = tool_context.state
    state['user:wave_height'] = height
    
    return {
        'action': 'save_wave_height',
        'value': height,
        'message': f'Saved wave height: {height}'
    }

def save_experience_level(level: str, tool_context: ToolContext) -> dict:
    state = tool_context.state
    state['user:experience_level'] = level
    
    return {
        'action': 'save_experience_level',
        'value': level,
        'message': f'Saved level of experiencie: {level}'
    }

def get_coordinates_tool(user_location: str) -> dict:
    geolocator = Nominatim(user_agent="BlueCastApp")
    location = geolocator.geocode(user_location)
    logger.info(f"Geocoded {user_location} to {location.latitude}, {location.longitude}")
    return {
        "latitude": location.latitude,
        "longitude": location.longitude,
        "place": location.address,
    }

def get_marine_forecast_tool(latitude: float, longitude: float) -> dict:
    url = "https://marine-api.open-meteo.com/v1/marine"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": "wave_height,wave_direction,wave_period",
        "forecast_days": 3,
    }

    response = requests.get(url, params=params)
    data = response.json()
    logger.info(f"Retrieved marine forecast for {latitude}, {longitude}")

    return data

# =============================================================================
# AGENT: PreferencesAgent - Get user surf preferences
# =============================================================================
preferences_agent = LlmAgent(
    name="PreferencesCollectorAgent",
    model=MODEL,
    description="Collect user surf preferences such as wave height, wave type, and experience level.",
    instruction="""
        You are a surf expert in charge of learning the user’s preferences.

        Your ONLY task is to collect this information naturally and in a friendly way:

        **REQUIRED** (without this we can’t search):

        * Preferred wave height (1–2m, 2–3m, 3–4m, etc.)
        * Type of wave (beach break, reef break, point break)
        * Experience level (beginner, intermediate, advanced)

        **OPTIONAL** (improves recommendations):

        * Swell direction
        * Wind preference (offshore, onshore, cross-shore)

        **Current preference status:**

        * Wave height: {wave_height}
        * Experience level: {experience_level}

        **IMPORTANT:**

        * Use the same language as the user
        * Keep the conversation natural, DO NOT make it sound like an interrogation
        * Use the tools to SAVE each preference when the user mentions it
        * After saving each preference, check if all are complete
        * When preferences are complete, let the user know that we can start searching
        * DO NOT search for conditions yourself, only collect preferences

        **Example conversation:**
        User: “I like waves around 1–2 meters.”
        You: [save with save_wave_height] “Perfect! Waves of 1–2m noted. What kind of waves do you prefer — beach break, reef break, or point break?”
    """,
    tools=[
        FunctionTool(save_wave_height),
        FunctionTool(save_experience_level),
        FunctionTool(check_preferences_complete),
    ],
)

# =============================================================================
# AGENT: GeocodingAgent - Get location coordinates
# =============================================================================
geocoding_agent = LlmAgent(
    name="GeocodingAgent",
    model=MODEL,
    tools = [get_coordinates_tool],
    instruction="""You are an agent specialized in obtaining geographic coordinates.

        MANDATORY PROCESS:
        1. Identify the name of the place in the user's query
        2. Execute the tool to get the coordinates of the place
        3. Return the coordinates in the specified format
        4. If the coordinates cannot be found, keep asking the user for clarification
        CORRECT RESPONSE EXAMPLE:
        latitude: 43.3183, longitude: -1.9812, place: San Sebastián

        IMPORTANT: 
        * Use the same language as the user
        * Your answer MUST contain exactly that format with the numbers and the place name.
    """,
    output_key="coordinates",
    description="Get geographical coordinates using GeoPy.",
)

# =============================================================================
# AGENT: MarineForecastAgent
# =============================================================================
marine_forecast_agent = LlmAgent(
    name="MarineForecastAgent",
    model=MODEL,
    tools=[get_marine_forecast_tool],
    instruction="""You are an agent specialized in obtaining marine weather forecasts.
        MANDATORY PROCESS:
        1. Extract latitude and longitude from the user's query.
        2. Execute the tool to get the marine weather forecast.
        3. Return the marine weather forecast in JSON format.
    """,
    output_key="marine_forecast",
    description="Get marine weather forecast using Marine API from Open Meteo.",
)

# =============================================================================
# AGENT: SurfCoach - Provide surf advice based on forecast
# =============================================================================
surf_coach_agent = LlmAgent(
    name="SurfCoachAgent",
    model=MODEL,
    instruction="""You are a surf coach agent that provides surf forecast based on 
    marine weather forecasts.
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
        
        IMPORTANT:
        * Use the same language as the user
    """,
    output_key="surf_forecast",
    description="Provide surf forecast based on marine weather forecast.",
)

# =============================================================================
# Agents pipeline
# =============================================================================
forecast_agents_pipeline = SequentialAgent(
    name="ForecastAgentsPipeline",
    sub_agents=[geocoding_agent, marine_forecast_agent, surf_coach_agent],
    description="Pipeline to get surf forecast based on user location.",
)

# =============================================================================
# Root agent
# =============================================================================
#root_agent = agents_pipeline

root_agent = Agent(
    name="RootSurfForecastAgent",
    model=MODEL,
    sub_agents=[preferences_agent, forecast_agents_pipeline],
    description="Root agent for surf forecast application.",
    instruction="""You are a surf coach agent that provides surf advice based on marine weather forecasts
    user preferences and location.
    MANDATORY PROCESS:
    1. First, collect user surf preferences using the PreferencesCollectorAgent. Keep asking until all
    required preferences are collected (wave height, experience level). Once you have all preferences, 
    don't ask anymmore about them to the user.
    2. Next, ask the user for the location to surf.
    3. Get surf forecast using the ForecastAgentsPipeline.
    3. Finally, provide surf advice based on the surf forecast and user preferences.
    and user preferences.

    IMPORTANT: Provide your final answer including:

        1. Use same language as the user. Don't use emojis, or at least gender related ones.
        2. A friendly greeting mentioning the full location
        3. The forecast dates and times
        4. A clear explanation of the wave conditions and their evolution over the day
        5. A recommendation about whether it’s a good day to surf and for what level
        6. A motivating comment

    Use a **warm and enthusiastic tone**, like a surfer friend giving advice.
    """,
)

# =============================================================================
# Runner
# =============================================================================
async def main():
    """Main function to run the agent."""
    load_dotenv()
    session_service = InMemorySessionService()
    runner = Runner(
        agent=root_agent, app_name=APP_NAME, session_service=session_service
    )
    user_id = "user_" + str(uuid.uuid4())[:8]
    session_id = "session_" + str(uuid.uuid4())[:8]

    await session_service.create_session(
        app_name=APP_NAME,
        user_id=user_id,
        session_id=session_id,
        state={
            "wave_height": None,
            "experience_level": None,
            "preferences_complete": False,
        },
    )

    while True:
        user_message = input("User>>: ")
        if user_message.lower() in ["exit", "quit"]:
            break

        content = types.Content(role="user", parts=[types.Part(text=user_message)])

        final_response = ""
        async for event in runner.run_async(
            user_id=user_id, session_id=session_id, new_message=content
        ):
            if event.is_final_response():
                if event.content and event.content.parts and event.content.parts[0].text:
                    final_response = event.content.parts[0].text
        
        print(f"Agent: {final_response}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting chat.")
