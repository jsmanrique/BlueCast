# BlueCast

Simple agentic AI-based service to get surf swell forecasts using Google ADK (Agent Development Kit).

## Overview

BlueCast is an intelligent surf forecasting application that uses a multi-agent architecture powered by Google's Gemini AI to provide personalized surf advice based on real-time marine weather conditions and user preferences.

## Architecture

BlueCast implements a **sequential pipeline** consisting of four specialized agents that work together to deliver comprehensive surf forecasts:

```
User Query → PreferencesCollectorAgent → GeocodingAgent → MarineForecastAgent → SurfCoachAgent → Final Advice
```

### Agent Pipeline Components

#### 1. PreferencesCollectorAgent
**Purpose:** Collects user surf preferences to provide personalized recommendations

- **Model:** gemini-2.5-flash-lite
- **Tools:**
  - `save_wave_height(height: str)`: Saves preferred wave height (1-2m, 2-3m, 3-4m, etc.)
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
