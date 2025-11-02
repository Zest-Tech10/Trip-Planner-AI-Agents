import os
import logging
import traceback
from datetime import date, datetime
from functools import lru_cache
from typing import Optional

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from crewai import Crew, LLM
from trip_agents import TripAgents
from trip_tasks import TripTasks

# ============================================================
# 🌍 ENVIRONMENT SETUP
# ============================================================
load_dotenv()

# ============================================================
# 🔧 LOGGING CONFIGURATION
# ============================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("vacAIgent_api.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
logger.info("🚀 VacAIgent API starting...")

# ============================================================
# 🚀 FASTAPI CONFIGURATION
# ============================================================
app = FastAPI(
    title="VacAIgent API",
    description="AI-powered travel planning API using CrewAI with Gemini → OpenAI fallback logic",
    version="1.1.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ⚠️ Replace with trusted origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# 📦 DATA MODELS
# ============================================================

class TripRequest(BaseModel):
    origin: str = Field(..., example="Bangalore, India", description="Your current location")
    destination: str = Field(..., example="Krabi, Thailand", description="Destination city and country")
    start_date: date = Field(..., example="2025-06-01", description="Start date of your trip")
    end_date: date = Field(..., example="2025-06-10", description="End date of your trip")
    interests: str = Field(..., example="2 adults who love swimming, hiking, shopping, and local food", description="Describe your interests and travel preferences")


class TripResponse(BaseModel):
    status: str
    message: str
    itinerary: Optional[str] = None
    error: Optional[str] = None


# ============================================================
# ⚙️ SETTINGS AND DEPENDENCIES
# ============================================================

class Settings:
    def __init__(self):
        self.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        self.SERPER_API_KEY = os.getenv("SERPER_API_KEY")
        self.BROWSERLESS_API_KEY = os.getenv("BROWSERLESS_API_KEY")


@lru_cache()
def get_settings():
    return Settings()


def validate_api_keys(settings: Settings = Depends(get_settings)):
    """Ensure all required API keys exist before running."""
    required_keys = {
        'GEMINI_API_KEY': settings.GEMINI_API_KEY,
        'OPENAI_API_KEY': settings.OPENAI_API_KEY,
        'SERPER_API_KEY': settings.SERPER_API_KEY,
        'BROWSERLESS_API_KEY': settings.BROWSERLESS_API_KEY
    }
    missing = [k for k, v in required_keys.items() if not v]
    if missing:
        logger.error(f"❌ Missing API keys: {', '.join(missing)}")
        raise HTTPException(status_code=500, detail=f"Missing required API keys: {', '.join(missing)}")
    return settings


# ============================================================
# 🧩 LLM FALLBACK HANDLER
# ============================================================

class LLMFallbackHandler:
    """Handles automatic fallback between Gemini and OpenAI models."""

    def __init__(self, settings: Settings):
        self.gemini_key = settings.GEMINI_API_KEY
        self.openai_key = settings.OPENAI_API_KEY

    def create_llm(self, provider: str):
        """Create an LLM client for a specific provider."""
        try:
            if provider == "gemini":
                logger.info("🧠 Using Gemini (Primary LLM)")
                return LLM(model="gemini/gemini-2.5-flash", api_key=self.gemini_key)
            elif provider == "openai":
                logger.info("🪄 Switching to OpenAI (Fallback LLM)")
                return LLM(model="gpt-5-mini", api_key=self.openai_key)
            else:
                raise ValueError("Invalid LLM provider")
        except Exception as e:
            logger.error(f"⚠️ Failed to initialize {provider}: {e}")
            raise

    def try_with_fallback(self, func, *args, **kwargs):
        """Try Gemini first → fallback to OpenAI on failure."""
        try:
            llm = self.create_llm("gemini")
            return func(llm, *args, **kwargs)
        except Exception as gemini_err:
            logger.warning(f"⚠️ Gemini failed: {gemini_err}")
            traceback.print_exc()

            try:
                llm = self.create_llm("openai")
                logger.info("🔁 Retrying with OpenAI fallback...")
                return func(llm, *args, **kwargs)
            except Exception as openai_err:
                logger.critical(f"❌ Both Gemini and OpenAI failed: {openai_err}")
                traceback.print_exc()
                raise HTTPException(status_code=500, detail=str(openai_err))


# ============================================================
# 🧳 TRIP CREW LOGIC
# ============================================================

class TripCrew:
    """Manages the CrewAI-based itinerary generation process."""

    def __init__(self, origin, destination, date_range, interests, settings: Settings):
        self.origin = origin
        self.destination = destination
        self.date_range = date_range
        self.interests = interests
        self.llm_handler = LLMFallbackHandler(settings)

    def _generate_itinerary(self, llm):
        """Internal CrewAI orchestration logic."""
        agents = TripAgents(llm=llm)
        tasks = TripTasks()

        # Create agents
        city_selector = agents.city_selection_agent()
        local_expert = agents.local_expert()
        concierge = agents.travel_concierge()

        # Create tasks
        identify_task = tasks.identify_task(city_selector, self.origin, self.destination, self.interests, self.date_range)
        gather_task = tasks.gather_task(local_expert, self.origin, self.interests, self.date_range)
        plan_task = tasks.plan_task(concierge, self.origin, self.interests, self.date_range)

        # Combine into a crew
        crew = Crew(
            agents=[city_selector, local_expert, concierge],
            tasks=[identify_task, gather_task, plan_task],
            verbose=True,
        )

        result = crew.kickoff()

        if hasattr(result, "output_text"):
            return result.output_text
        elif hasattr(result, "final_output"):
            return result.final_output
        return str(result)

    def run(self):
        """Run trip generation with automatic LLM fallback."""
        return self.llm_handler.try_with_fallback(self._generate_itinerary)


# ============================================================
# 🌐 API ROUTES
# ============================================================

@app.get("/")
async def root():
    return {
        "message": "Welcome to VacAIgent API 🚀",
        "docs_url": "/docs",
        "version": "1.1.0"
    }


@app.post("/api/v1/plan-trip", response_model=TripResponse)
async def plan_trip(
    trip_request: TripRequest,
    settings: Settings = Depends(validate_api_keys)
):
    """Generate a personalized travel itinerary."""
    logger.info(f"🧳 Received trip planning request: {trip_request}")

    if trip_request.end_date <= trip_request.start_date:
        raise HTTPException(status_code=400, detail="End date must be after start date")

    date_range = f"{trip_request.start_date} to {trip_request.end_date}"

    try:
        trip_crew = TripCrew(
            trip_request.origin,
            trip_request.destination,
            date_range,
            trip_request.interests,
            settings
        )

        itinerary = trip_crew.run()

        logger.info("✅ Trip itinerary successfully generated.")
        return TripResponse(
            status="success",
            message="Trip plan generated successfully",
            itinerary=itinerary
        )

    except HTTPException as e:
        logger.error(f"❌ HTTP Error: {e.detail}")
        raise e
    except Exception as e:
        logger.exception("❌ Unexpected error during itinerary generation.")
        return TripResponse(
            status="error",
            message="Failed to generate trip plan",
            error=str(e)
        )


@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


# ============================================================
# 🚀 ENTRY POINT
# ============================================================
if __name__ == "__main__":
    import uvicorn
    logger.info("✅ Starting VacAIgent FastAPI server on port 8000...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
