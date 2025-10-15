from fastapi import FastAPI, HTTPException, Depends, WebSocket
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional
from crewai import Crew, LLM
from trip_agents import TripAgents
from trip_tasks import TripTasks
import os
import asyncio
from dotenv import load_dotenv
from functools import lru_cache

# ======================== Load Environment ======================== #
load_dotenv()

app = FastAPI(
    title="VacAIgent API",
    description="AI-powered travel planning API using CrewAI",
    version="1.0.0"
)

# ======================== CORS Setup ======================== #
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # In production, restrict to frontend URL
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # ✅ Replace * with frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Type", "Cache-Control"],  # ✅ Important for SSE
)


# ======================== Models ======================== #
class TripRequest(BaseModel):
    origin: str = Field(..., example="Bangalore, India")
    destination: str = Field(..., example="Krabi, Thailand")
    start_date: date = Field(..., example="2025-06-01")
    end_date: date = Field(..., example="2025-06-10")
    interests: str = Field(..., example="2 adults who love swimming, dancing, hiking, shopping, local food, and water sports")

class TripResponse(BaseModel):
    status: str
    message: str
    itinerary: Optional[str] = None
    error: Optional[str] = None

# ======================== Settings ======================== #
class Settings:
    def __init__(self):
        self.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        self.SERPER_API_KEY = os.getenv("SERPER_API_KEY")
        self.BROWSERLESS_API_KEY = os.getenv("BROWSERLESS_API_KEY")

@lru_cache()
def get_settings():
    return Settings()

def validate_api_keys(settings: Settings = Depends(get_settings)):
    required_keys = {
        'GEMINI_API_KEY': settings.GEMINI_API_KEY,
        'SERPER_API_KEY': settings.SERPER_API_KEY,
        'BROWSERLESS_API_KEY': settings.BROWSERLESS_API_KEY
    }
    missing = [k for k, v in required_keys.items() if not v]
    if missing:
        raise HTTPException(status_code=500, detail=f"Missing API keys: {', '.join(missing)}")
    return settings

# ======================== Trip Crew ======================== #
class TripCrew:
    def __init__(self, origin, destination, date_range, interests):
        self.destination = destination
        self.origin = origin
        self.interests = interests
        self.date_range = date_range
        self.llm = LLM(model="gemini/gemini-2.5-flash")

    def run(self):
        agents = TripAgents(llm=self.llm)
        tasks = TripTasks()

        city_selector = agents.city_selection_agent()
        local_expert = agents.local_expert()
        travel_concierge = agents.travel_concierge()

        identify_task = tasks.identify_task(city_selector, self.origin, self.destination, self.interests, self.date_range)
        gather_task = tasks.gather_task(local_expert, self.origin, self.interests, self.date_range)
        plan_task = tasks.plan_task(travel_concierge, self.origin, self.interests, self.date_range)

        crew = Crew(
            agents=[city_selector, local_expert, travel_concierge],
            tasks=[identify_task, gather_task, plan_task],
            verbose=True
        )

        result = crew.kickoff()
        if hasattr(result, 'output_text'):
            return result.output_text
        elif hasattr(result, 'final_output'):
            return result.final_output
        else:
            return str(result)

# ======================== Routes ======================== #
@app.get("/")
async def root():
    return {"message": "Welcome to VacAIgent API"}

@app.get("/api/v1/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# ---------- Standard Non-Streaming Endpoint ---------- #
@app.post("/api/v1/plan-trip", response_model=TripResponse)
async def plan_trip(trip_request: TripRequest, settings: Settings = Depends(validate_api_keys)):
    if trip_request.end_date <= trip_request.start_date:
        raise HTTPException(status_code=400, detail="End date must be after start date")

    date_range = f"{trip_request.start_date} to {trip_request.end_date}"

    try:
        trip_crew = TripCrew(trip_request.origin, trip_request.destination, date_range, trip_request.interests)
        itinerary = trip_crew.run()
        return TripResponse(status="success", message="Trip plan generated successfully", itinerary=itinerary)
    except Exception as e:
        return TripResponse(status="error", message="Failed to generate trip plan", error=str(e))

# ---------- Streaming Endpoint (Server-Sent Events) ---------- #
# @app.post("/api/v1/stream-trip")
# async def stream_trip(trip_request: TripRequest, settings: Settings = Depends(validate_api_keys)):
#     """Streams live progress logs as the LLM processes."""
#     if trip_request.end_date <= trip_request.start_date:
#         raise HTTPException(status_code=400, detail="End date must be after start date")

#     date_range = f"{trip_request.start_date} to {trip_request.end_date}"

#     async def event_stream():
#         try:
#             yield "data: 🤖 Initializing trip planning system...\n\n"
#             await asyncio.sleep(1)

#             yield f"data: 🌍 Gathering information for {trip_request.destination}...\n\n"
#             await asyncio.sleep(1)

#             yield "data: 🧭 Analyzing preferences and constraints...\n\n"
#             await asyncio.sleep(1)

#             yield "data: ✈️ Generating optimized itinerary using CrewAI agents...\n\n"
#             await asyncio.sleep(1)

#             trip_crew = TripCrew(trip_request.origin, trip_request.destination, date_range, trip_request.interests)
#             itinerary = trip_crew.run()

#             yield "data: ✅ Trip planning complete!\n\n"
#             yield f"data: {itinerary}\n\n"

#         except Exception as e:
#             yield f"data: ❌ Error: {str(e)}\n\n"

#     return StreamingResponse(event_stream(), media_type="text/event-stream")

@app.post("/api/v1/stream-trip")
async def stream_trip(trip_request: TripRequest, settings: Settings = Depends(validate_api_keys)):
    async def event_stream():
        try:
            yield "data: 🤖 Initializing trip planning system...\n\n"
            await asyncio.sleep(1)
            yield f"data: 🌍 Gathering information for {trip_request.destination}...\n\n"
            await asyncio.sleep(1)
            yield "data: 🧭 Analyzing preferences and constraints...\n\n"
            await asyncio.sleep(1)
            yield "data: ✈️ Generating optimized itinerary using CrewAI agents...\n\n"
            await asyncio.sleep(1)
            yield "data: ✅ Trip planning complete!\n\n"
        except Exception as e:
            yield f"data: ❌ Error: {str(e)}\n\n"

    # ✅ Explicit headers for SSE
    headers = {
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Content-Type": "text/event-stream",
        "Access-Control-Allow-Origin": "*",
    }

    return StreamingResponse(event_stream(), media_type="text/event-stream", headers=headers)

# ---------- WebSocket Streaming Endpoint ---------- #
@app.websocket("/ws/stream")
async def websocket_stream(websocket: WebSocket):
    """WebSocket endpoint for real-time travel planning updates."""
    await websocket.accept()
    messages = [
        "🔍 Querying travel recommendations...",
        "🧠 Analyzing your preferences...",
        "📅 Optimizing itinerary...",
        "💰 Estimating budget...",
        "🏖️ Selecting top experiences...",
        "✅ Plan ready to deliver!"
    ]
    try:
        for msg in messages:
            await websocket.send_text(msg)
            await asyncio.sleep(2)  # simulate delay
    except Exception as e:
        await websocket.send_text(f"❌ WebSocket error: {str(e)}")
    finally:
        await websocket.close()

# ======================== Run ======================== #
if __name__ == "__main__":
    import uvicorn
    # uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
    uvicorn.run("jahid:app", host="0.0.0.0", port=8000, reload=True)
