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

## ⚖️ Solution Report and Solution Demo Video

- The solution report includes overview, solution, and vulnerability and risk.
- The solution demo video shows the working app, accessible via api call.

## 🔌 API

1. Document  
   `POST /add`: to add a new document to the knowledge base.

   ```bash
    curl -X POST "http://localhost:8000/add" \
    -H "Content-Type: application/json" \
    -d '{"text": "{text}"}'
   ```

2. Query  
   `POST /ask`: to run a full retrieval-augmented generation query.

   ```bash
    curl -X POST "http://127.0.0.1:8000/ask" \
    -H "Content-Type: application/json" \
    -d '{"question": "{question}"}'
   ```

3. Status  
   `GET /status`: to check status of Qdrant, in-memory document, and LangGraph workflow.
   ```bash
    curl "http://127.0.0.1:8000/status"
   ```

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
