import streamlit as st
from crewai import Crew, LLM
from trip_agents2 import TripAgents, StreamToExpander
from trip_tasks import TripTasks
import datetime
import sys
from langchain_openai import OpenAI




def icon(emoji: str):
    """Shows an emoji as a Notion-style page icon."""
    st.write(
        f'<span style="font-size: 78px; line-height: 1">{emoji}</span>',
        unsafe_allow_html=True,
    )

class TripCrew:
    def __init__(self, origin, cities, date_range, interests):
        self.cities = cities
        self.origin = origin
        self.interests = interests
        self.date_range = f"{date_range[0].strftime('%Y-%m-%d')} to {date_range[1].strftime('%Y-%m-%d')}"
        self.output_placeholder = st.empty()
        
        # Access API keys from Streamlit secrets
        # self.gemini_api_key = st.secrets["GEMINI_API_KEY"]
        self.openai_api_key = st.secrets["OPENAI_API_KEY"]  # 
        self.browserless_api_key = st.secrets["BROWSERLESS_API_KEY"]
        self.serper_api_key = st.secrets["SERPER_API_KEY"]
        
        # Pass the keys to your LLM and agents as needed
        # self.llm = LLM(model="gemini/gemini-2.5-flash")
        self.llm = LLM(model="gpt-4o", api_key=self.openai_api_key)

        # You'll need to update your TripAgents and TripTasks to accept these keys
        # For example, you might modify the agent initialization to pass the keys:
        # self.agents = TripAgents(llm=self.llm, browserless_api_key=self.browserless_api_key, serper_api_key=self.serper_api_key)

    

    def run(self):
        try:
            agents = TripAgents(llm=self.llm)
            tasks = TripTasks()

            city_selector_agent = agents.city_selection_agent()
            local_expert_agent = agents.local_expert()
            travel_concierge_agent = agents.travel_concierge()

            identify_task = tasks.identify_task(
                city_selector_agent,
                self.origin,
                self.cities,
                self.interests,
                self.date_range
            )

            gather_task = tasks.gather_task(
                local_expert_agent,
                self.origin,
                self.interests,
                self.date_range
            )

            plan_task = tasks.plan_task(
                travel_concierge_agent,
                self.origin,
                self.interests,
                self.date_range
            )

            crew = Crew(
                agents=[
                    city_selector_agent, local_expert_agent, travel_concierge_agent
                ],
                tasks=[identify_task, gather_task, plan_task],
                verbose=True
            )

            result = crew.kickoff()
            self.output_placeholder.markdown(result)
            return result
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            return None


if __name__ == "__main__":
    icon("🏖️ Trip-Planner-AI-Agents")

    st.subheader("Let AI agents plan your next vacation!",
                 divider="rainbow", anchor=False)

    import datetime

    today = datetime.datetime.now().date()
    next_year = today.year + 1
    jan_16_next_year = datetime.date(next_year, 1, 10)

    with st.sidebar:
        st.header("👇 Enter your trip details")
        with st.form("my_form"):
            location = st.text_input(
                "Where are you currently located?", placeholder="Kualalumpur, Malaysia")
            cities = st.text_input(
                "City and country are you interested in vacationing at?", placeholder="Rome, Italy")
            date_range = st.date_input(
                "Date range you are interested in traveling?",
                min_value=today,
                value=(today, jan_16_next_year + datetime.timedelta(days=6)),
                format="MM/DD/YYYY",
            )
            interests = st.text_area("High level interests and hobbies or extra details about your trip?",
                                     placeholder="2 adults who love swimming, dancing, hiking, and eating")

            submitted = st.form_submit_button("Submit")

        st.divider()

        

if submitted:
    with st.status("🤖 **Agents at work...**", state="running", expanded=True) as status:
        with st.container(height=500, border=False):
            sys.stdout = StreamToExpander(st)
            trip_crew = TripCrew(location, cities, date_range, interests)
            result = trip_crew.run()
        status.update(label="✅ Trip Plan Ready!",
                      state="complete", expanded=False)

    st.subheader("Here is your Trip Plan", anchor=False, divider="rainbow")
    st.markdown(result)
