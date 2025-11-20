# BlueCast

Simple agentic AI-based service to get surf swell forecasts using Google ADK (Agent Development Kit).

## Overview

BlueCast is an intelligent surf forecasting application that uses a multi-agent architecture powered by Google's Gemini AI to provide personalized surf advice based on real-time marine weather conditions.

## Architecture

BlueCast implements a **sequential agent pipeline** consisting of three specialized agents that work together to deliver comprehensive surf forecasts:

```
User Query → GeocodingAgent → MarineForecastAgent → SurfCoachAgent → Final Advice
```

### Agent Pipeline Components

#### 1. GeocodingAgent
**Purpose:** Converts location names to geographic coordinates

- **Model:** gemini-2.5-flash-lite
- **Tool:** `get_coordinates_tool(location: str)`
  - Uses Open-Meteo Geocoding API
  - Returns latitude, longitude, and place name
- **Output:** Coordinates in format: `latitude: X, longitude: Y, place: Name`

#### 2. MarineForecastAgent
**Purpose:** Retrieves marine weather forecast data

- **Model:** gemini-2.5-flash-lite
- **Tool:** `get_marine_forecast_tool(latitude: float, longitude: float)`
  - Uses Open-Meteo Marine API
  - Fetches 3-day forecast with hourly data
  - Returns wave height, wave direction, and wave period
- **Output:** JSON-formatted marine forecast data

#### 3. SurfCoachAgent
**Purpose:** Provides personalized surf advice

- **Model:** gemini-2.5-flash-lite
- **Analysis:** Interprets wave conditions based on:
  - **Wave Height:**
    - 0.3-0.8m: Ideal for beginners
    - 0.8-1.5m: Good for intermediate surfers
    - 1.5-2.5m: For advanced surfers
    - \>2.5m: Experts only
  - **Wave Period:**
    - <6s: Short, choppy waves
    - 6-10s: Good conditions
    - 10-14s: Excellent quality swell
    - \>14s: Powerful, consistent waves
  - **Wave Direction:** Cardinal directions (N/E/S/W)
- **Output:** Friendly, personalized surf advice with recommendations

### Technical Stack

- **Framework:** Google ADK (Agent Development Kit)
- **AI Model:** Gemini 2.5 Flash Lite
- **Session Management:** In-memory session service
- **External APIs:**
  - Open-Meteo Geocoding API
  - Open-Meteo Marine API

### Configuration

```python
APP_NAME = "surf_forecast_app"
MODEL = "gemini-2.5-flash-lite"
```

The system includes retry configuration for robust API calls:
- Maximum 5 retry attempts
- Handles HTTP errors: 429, 500, 503, 504
- Exponential backoff with base 7

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

3. Set up your Google API credentials in a `.env` file (if required)

## Running BlueCast

BlueCast can be run using Google ADK in two different modes:

### CLI Mode

Run the agent in command-line interface mode:

```bash
adk run BlueCast
```

This will start an interactive session where you can chat with the surf forecasting agent.

**Example interaction:**
```
User: What are the surf conditions in San Sebastián?
BlueCast: [Provides detailed surf forecast for San Sebastián]
```

### Web Interface Mode

Launch the web interface on a specific port:

```bash
adk web --port 8000
```

Then open your browser and navigate to:
```
http://localhost:8000
```

The web interface provides a user-friendly chat interface to interact with the BlueCast agent.

## Usage Example

Simply ask about surf conditions in any location:

- "What are the surf conditions in Mundaka today?"
- "Is it good for surfing in Zarautz tomorrow?"
- "Give me the surf forecast for Hossegor"

The agent will:
1. Find the coordinates of the location
2. Retrieve the marine forecast
3. Provide personalized surf advice based on your skill level and the conditions

## Features

- 🌊 Real-time surf forecasts for any coastal location
- 🤖 Multi-agent AI architecture for accurate analysis
- 📊 3-day hourly wave predictions
- 🏄 Skill-level-based recommendations
- 🌍 Multilingual support (responds in user's language)
- 💬 Friendly, enthusiastic surf coach personality

## License

See [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
