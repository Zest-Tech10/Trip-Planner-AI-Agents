import streamlit as st
from crewai import Crew, LLM
# from trip_agents2 import TripAgents, StreamToExpander
from trip_agents import TripAgents, StreamToExpander
from trip_tasks import TripTasks
import datetime
import sys
import traceback
import asyncio
import nest_asyncio  # ✅ FIX added

from langchain_openai import OpenAI

nest_asyncio.apply()  # ✅ Allows asyncio.run() inside Streamlit

# --------------------------
# Helper: display emoji
# --------------------------
def icon(emoji: str):
    """Shows an emoji as a Notion-style page icon."""
    st.write(
        f'<span style="font-size: 78px; line-height: 1">{emoji}</span>',
        unsafe_allow_html=True,
    )


# --------------------------
# TripCrew class with dynamic LLM fallback
# --------------------------
class TripCrew:
    def __init__(self, origin, cities, date_range, interests):
        self.cities = cities
        self.origin = origin
        self.interests = interests
        self.date_range = f"{date_range[0].strftime('%Y-%m-%d')} to {date_range[1].strftime('%Y-%m-%d')}"
        self.output_placeholder = st.empty()

        # Get API keys from secrets
        self.gemini_api_key = st.secrets["GEMINI_API_KEY"]
        self.openai_api_key = st.secrets["OPENAI_API_KEY"]
        self.browserless_api_key = st.secrets["BROWSERLESS_API_KEY"]
        self.serper_api_key = st.secrets["SERPER_API_KEY"]

        # Initialize Gemini as the primary model
        self.llm = self.create_llm("gemini")

    def create_llm(self, provider="gemini"):
        """Create LLM instance for Gemini or OpenAI."""
        try:
            if provider == "gemini":
                st.info("🧠 Using Gemini (Primary LLM)...")
                llm = LLM(model="gemini/gemini-2.5-flash", api_key=self.gemini_api_key)
            elif provider == "openai":
                st.info("🪄 Switching to OpenAI (Fallback)...")
                llm = LLM(model="gpt-5-mini", api_key=self.openai_api_key)
            else:
                raise ValueError("Invalid LLM provider")
            return llm
        except Exception as e:
            st.error(f"Failed to initialize {provider}: {str(e)}")
            raise

    async def try_run_with_llm(self, llm):
        """Run the crew process using a given LLM."""
        agents = TripAgents(llm=llm)
        tasks = TripTasks()

        city_selector_agent = agents.city_selection_agent()
        local_expert_agent = agents.local_expert()
        travel_concierge_agent = agents.travel_concierge()

        identify_task = tasks.identify_task(
            city_selector_agent,
            self.origin,
            self.cities,
            self.interests,
            self.date_range,
        )

        gather_task = tasks.gather_task(
            local_expert_agent,
            self.origin,
            self.interests,
            self.date_range,
        )

        plan_task = tasks.plan_task(
            travel_concierge_agent,
            self.origin,
            self.interests,
            self.date_range,
        )

        crew = Crew(
            agents=[city_selector_agent, local_expert_agent, travel_concierge_agent],
            tasks=[identify_task, gather_task, plan_task],
            verbose=True,
 
        )

        result = crew.kickoff()
    
        return result

    def run(self):
        """Run trip planning with automatic Gemini → OpenAI fallback."""
        try:
            # --- Attempt 1: Gemini ---
            result = asyncio.run(self.try_run_with_llm(self.llm))
            self.output_placeholder.markdown(result)
            return result

        except Exception as gemini_error:
            st.warning(f"⚠️ Gemini failed: {str(gemini_error)}")
            traceback.print_exc()

            # --- Attempt 2: Fallback to OpenAI ---
            try:
                fallback_llm = self.create_llm("openai")
                result = asyncio.run(self.try_run_with_llm(fallback_llm))
                st.success("✅ Successfully continued with OpenAI fallback.")
                self.output_placeholder.markdown(result)
                return result

            except Exception as openai_error:
                st.error(f"❌ Both Gemini and OpenAI failed.\n{openai_error}")
                traceback.print_exc()
                return None


# --------------------------
# Streamlit UI
# --------------------------
if __name__ == "__main__":
    icon("🏖️ Trip-Planner-AI-Agents")

    st.subheader(
        "Let AI agents plan your next vacation!",
        divider="rainbow",
        anchor=False,
    )

    today = datetime.datetime.now().date()
    next_year = today.year + 1
    jan_16_next_year = datetime.date(next_year, 1, 10)

    with st.sidebar:
        st.header("👇 Enter your trip details")
        with st.form("my_form"):
            location = st.text_input(
                "Where are you currently located?", placeholder="Kuala Lumpur, Malaysia"
            )
            cities = st.text_input(
                "City and country are you interested in vacationing at?",
                placeholder="Rome, Italy",
            )
            date_range = st.date_input(
                "Date range you are interested in traveling?",
                min_value=today,
                value=(today, jan_16_next_year + datetime.timedelta(days=6)),
                format="MM/DD/YYYY",
            )
            interests = st.text_area(
                "High level interests and hobbies or extra details about your trip?",
                placeholder="2 adults who love swimming, dancing, hiking, and eating",
            )

            submitted = st.form_submit_button("Submit")

        st.divider()

# --------------------------
# Run trip planner after submission
# --------------------------
if "submitted" in locals() and submitted:
    with st.status("🤖 **Agents at work...**", state="running", expanded=True) as status:
        with st.container(height=500, border=False):
            sys.stdout = StreamToExpander(st)
            trip_crew = TripCrew(location, cities, date_range, interests)
            result = trip_crew.run()
        status.update(label="✅ Trip Plan Ready!", state="complete", expanded=False)

    if result:
        st.subheader("Here is your Trip Plan", anchor=False, divider="rainbow")
        st.markdown(result)
    else:
        st.error("❌ Could not generate trip plan. Please check API keys or try again.")


