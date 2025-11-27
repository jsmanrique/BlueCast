# BlueCast

Simple agentic AI-based service to get surf swell forecasts using Google ADK (Agent Development Kit).

## Overview

BlueCast is an intelligent surf forecasting application that uses a multi-agent architecture powered by Google's Gemini AI to provide personalized surf advice based on real-time marine weather conditions and user preferences.

## Architecture

BlueCast implements a **sequential agent pipeline** consisting of four specialized agents that work together to deliver comprehensive surf forecasts:

```
User Query → PreferencesCollectorAgent → GeocodingAgent → MarineForecastAgent → SurfCoachAgent → Final Advice
```

### Agent Pipeline Components

#### 1. PreferencesCollectorAgent
**Purpose:** Collects user surf preferences to provide personalized recommendations

- **Model:** gemini-2.5-flash-lite
- **Tools:**
  - `save_wave_height(height: str)`: Saves preferred wave height (1-2m, 2-3m, 3-4m, etc.)
  - `save_wave_type(wave_type: str)`: Saves preferred wave type (beach break, reef break, point break)
  - `save_experience_level(level: str)`: Saves user experience level (beginner, intermediate, advanced)
  - `check_preferences_complete()`: Checks if all required preferences are collected
- **Process:** 
  - Collects required preferences: wave height, wave type, and experience level
  - Collects optional preferences: swell direction
  - Maintains natural conversation flow while gathering information
- **Output:** Complete user preferences stored in session state

#### 2. GeocodingAgent
**Purpose:** Converts location names to geographic coordinates

- **Model:** gemini-2.5-flash-lite
- **Tool:** `get_coordinates_tool(user_location: str)`
  - Uses Nominatim (GeoPy) for geocoding
  - Returns latitude, longitude, and place name
- **Output:** Coordinates in format: `latitude: X, longitude: Y, place: Name`

#### 3. MarineForecastAgent
**Purpose:** Retrieves marine weather forecast data

- **Model:** gemini-2.5-flash-lite
- **Tool:** `get_marine_forecast_tool(latitude: float, longitude: float)`
  - Uses Open-Meteo Marine API
  - Fetches 3-day forecast with hourly data
  - Returns wave height, wave direction, and wave period
- **Output:** JSON-formatted marine forecast data

#### 4. SurfCoachAgent
**Purpose:** Provides personalized surf advice based on user preferences and forecast data

- **Model:** gemini-2.5-flash-lite
- **Analysis:** Interprets wave conditions based on:
  - **Wave Height:**
    - 0.3-0.8m: Ideal for beginners
    - 0.8-1.5m: Good for intermediate surfers
    - 1.5-2.5m: For advanced surfers
    - >2.5m: Experts only
  - **Wave Period:**
    - <6s: Short, choppy waves
    - 6-10s: Good conditions
    - 10-14s: Excellent quality swell
    - >14s: Powerful, consistent waves
  - **Wave Direction:** Cardinal directions (N/E/S/W)
- **Output:** Friendly, personalized surf advice with recommendations matching user preferences

### Technical Stack

- **Framework:** Google ADK (Agent Development Kit)
- **AI Model:** Gemini 2.5 Flash Lite
- **Session Management:** In-memory session service
- **External APIs:**
  - Nominatim (GeoPy) for geocoding
  - Open-Meteo Marine API for weather data


### Configuration

```python
APP_NAME = "surf_forecast_app"
MODEL = "gemini-2.5-flash-lite"
```

### Environment Variables

Create a `.env` file with your Google API key:

```bash
GOOGLE_API_KEY="your-google-api-key-here"
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/jsmanrique/BlueCast.git
cd BlueCast
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your Google API credentials in a `.env` file:
```bash
echo 'GOOGLE_API_KEY="your-google-api-key-here"' > .env
```

## Running BlueCast

Run the agent directly using Python:

```bash
python agent.py
```

This will start an interactive session where you can chat with the surf forecasting agent.

**Example interaction:**
```
Hello there! Where do you want to go surfing? (Type exit to quit): San Sebastián
Agent: [Provides detailed surf forecast for San Sebastián]
```

The agent will:
1. First collect your surf preferences (wave height, wave type, experience level)
2. Find the coordinates of your location
3. Retrieve the marine forecast
4. Provide personalized surf advice based on your preferences and the conditions

## Usage Example

The conversation flow with BlueCast:

1. **Preference Collection:**
```
BlueCast: Hello there! Where do you want to go surfing? (Type exit to quit): San Sebastián
BlueCast: Perfect! I'll help you find the best spots in San Sebastián. First, let me learn about your preferences to give you the best recommendations.

What preferred wave height do you like? (1-2m, 2-3m, 3-4m, etc.)
User: 1-2m
BlueCast: Great! Waves of 1-2m noted. What kind of waves do you prefer - beach break, reef break, or point break?
User: beach break
BlueCast: Beach break it is! What's your experience level? (beginner, intermediate, advanced)
User: intermediate
BlueCast: Perfect! Now I have all the information I need. Let me check the surf conditions for you in San Sebastián...
```

2. **Forecast and Advice:**
```
BlueCast: [Provides detailed surf forecast for San Sebastián with personalized recommendations based on user preferences]
```

You can ask about any coastal location:
- "Mundaka"
- "Zarautz"
- "Hossegor"

## Features

- 🌊 Real-time surf forecasts for any coastal location
- 🤖 Multi-agent AI architecture for accurate analysis
- 📊 3-day hourly wave predictions
- 👤 Personalized recommendations based on user preferences
- 🏄 Skill-level-based recommendations
- 🌍 Multilingual support (responds in user's language)
- 💬 Friendly, enthusiastic surf coach personality
- 🗨️ Natural conversation flow for preference collection

## License

See [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
