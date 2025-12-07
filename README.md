# AssistX AI Engineer Test Case: Vacation Planner

This project implements a proof-of-concept AI vacation planner that can understand natural-language travel requests, interpret user preferences, check (mock) calendar availability, search for mock flights and hotels, and assemble a structured, day-by-day VacationPlan using an LLM-powered agent equipped with carefully defined tools. It also provides a dedicated booking endpoint that allows users to confirm a proposed itinerary once they explicitly approve it. The implementation combines FastAPI for the backend API, Pydantic v2 for data modeling and validation, PydanticAI for agent orchestration, OpenAI’s GPT-5-Nano for natural-language reasoning, and a lightweight in-memory storage layer to keep the proof-of-concept fully self-contained and easy to run.

[Click here to learn more about the project: assistx-vp/assets/Task - AI Engineer (LLM) Revised.pdf](<https://github.com/verneylmavt/assistx-vp/blob/fa8ebaab0b877b795af87f442eb632d78826cb3b/assets/Task%20-%20AI%20Engineer%20(LLM)%20Revised.pdf>).

## 📁 Project Structure

```
assistx-vp
│
├─ app/                              # Solution app
│  ├─ config.py                      # Configuration files
│  ├─ main.py                        # FastAPI app
│  │
│  ├─ agent/
│  │  └─ vacation_agent.py           # PydanticAI agent with tools
│  │
│  ├─ models/
│  │  ├─ api.py                      # API models
│  │  └─ domain.py                   # Domain models
│  │
│  ├─ services/
│  │  ├─ bookings.py                 # Booking service
│  │  ├─ calendar.py                 # Calendar service
│  │  ├─ preferences.py              # Preferences service
│  │  ├─ sessions.py                 # Session helper
│  │  └─ travel_search.py            # Travel search service (for mock flights/hotels)
│  │
│  └─ storage/
│     └─ in_memory.py                # In-memory storage
│
├─ assets/
│  ├─ vacation_planner_solution.pdf  # Solution report
│  └─ vacation_planner_demo.gif      # Solution demo video
│
├─ .env
└─ requirements.txt
```

## 💡 Solution Report and Solution Demo Video

- The solution report includes overview, solution, and vulnerability and risk. [Click here to learn more about the solution report: assistx-vp/assets/vacation_planner_solution.pdf](https://github.com/verneylmavt/assistx-vp/blob/392517c31b3a6190a7c442b79437368a83ac4b44/assets/vacation_planner_solution.pdf).
- The solution demo video shows the working app, accessible via api call. [Click here to learn more about the solution demo video: assistx-vp/assets/vacation_planner_demo.gif](https://github.com/verneylmavt/assistx-vp/blob/392517c31b3a6190a7c442b79437368a83ac4b44/assets/vacation_planner_demo.gif).

## 🔌 API

1. Health Check
   - `GET /health`: to verify that the backend is running correctly, responding to requests, and using the expected LLM configuration
     - Request: `None`
     - Response: `'status', 'model'`
     ```bash
     curl -s "http://localhost:8000/health"
     ```
2. User Preferences
   - `GET /api/preferences/{user_id}`: to retrieve the user’s saved travel preferences or automatically initialize defaults if none exist
     - Request: `user_id`
     - Response: `PreferencesResponse`
     ```bash
     curl -s "http://localhost:8000/api/preferences/{user_id}"
     ```
   - `PUT /api/preferences/{user_id}`: to update the user’s travel preferences with new budgets, origins, interests, or other settings
     - Request: `PreferencesUpdateRequest`
     - Response: `PreferencesResponse`
     ```bash
     curl -s -X PUT "http://localhost:8000/api/preferences/{user_id}" \
     -H "Content-Type: application/json" \
     -d '{
        "home_city": "{home_city}",
        "default_currency": "{default_currency}",
        "max_budget_total": {max_budget_total},
        "max_budget_per_day": {max_budget_per_day},
        "interests": ["{interest_1}", "{interest_i}", "{interest_n}"],
        "travel_style": "{travel_style}",
        "preferred_airlines": ["{preferred_airline_1}", "{preferred_airline_i}", "{preferred_airline_n}"],
        "preferred_hotel_types": ["{preferred_hotel_type_1}", "{preferred_hotel_type_i}", "{preferred_hotel_type_n}"]
     }'
     ```
   - `GET /api/video/first-frame/{video_source_id}`: to return the first frame of a specific video as a JPEG image
3. Polygon Area Management
   - `GET /api/areas`: to list all defined polygon areas used for people counting
     - Request: `None`
     - Response: `'status', 'model'`
     ```bash
     curl -s "http://localhost:8000/api/areas"
     ```
   - `POST /api/areas`: to create a new polygon detection area for a given video source
     - Request: `None`
     - Response: `'status', 'model'`
     ```bash
     curl -s -X POST http://localhost:8000/api/areas \
      -H "Content-Type: application/json" \
      -d '{
         "video_source_id": {video_source_id},
         "name": "{area_name}",
         "polygon": [
            {"x":{x1},"y":{y1}},
            {"x":{x2},"y":{y2}},
            {"x":{x3},"y":{y3}},
            {"x":{x4},"y":{y4}}
         ]
      }'
     ```
4. Real-Time Detection & Streaming
   - `GET /stream/{video_source_id}`: to run live object detection, tracking, and people counting on a selected video source
5. People Counting Statistics
   - `GET /api/stats/live`: to return live statistics of people movement for a specific video source and polygon area
     ```bash
     curl -s "http://localhost:8000/api/stats/live?video_source_id={video_source_id}&area_id={area_id}&window_seconds={window_seconds}"
     ```
   - `GET /api/stats`: to provide historical statistics for a given video source and area, aggregated over time buckets
     ```bash
     curl -s "http://localhost:8000/api/stats?video_source_id={video_source_id}&area_id={area_id}&granularity=minute&start={start_ISO_8601}&end={end_ISO_8601}"
     ```
6. Dashboard
   - `GET /dashboard`: to return an interactive HTML dashboard for testing and visualization

## ⚙️ Local Setup

0. Make sure to have the prerequisites:

   - Git
   - Python
   - Conda or venv
   - Docker

1. Clone the repository:

   ```bash
    git clone https://github.com/verneylmavt/bithealth-crfc.git
    cd bithealth-crfc
   ```

2. Create environment and install dependencies:

   ```bash
   conda create -n bithealth python=3.10 -y
   conda activate bithealth

   pip install -r requirements.txt
   ```

3. Start Docker Desktop and run Qdrant:

   ```bash
   docker run -p 6333:6333 -d qdrant/qdrant
   ```

4. Run the server:

   ```bash
   uvicorn app.main:app --reload
   ```

5. Open the dashboard:
   ```bash
   start "http://127.0.0.1:8000/dashboard"
   ```
