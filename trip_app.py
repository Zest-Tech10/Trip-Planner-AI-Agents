# import os
# import streamlit as st
# from crewai import Crew, LLM
# # from trip_agents2 import TripAgents, StreamToExpander
# from trip_agents import TripAgents, StreamToExpander
# from trip_tasks import TripTasks
# import datetime
# import sys
# import traceback
# import asyncio
# import nest_asyncio  # ✅ FIX added
# from langchain_openai import OpenAI
# import time

# # ✅ Enables asyncio.run() inside Streamlit
# nest_asyncio.apply()



# # --------------------------
# # Helper: display emoji
# # --------------------------
# def icon(emoji: str = "🌍"):
#     """Shows a simple colorful agent-style emoji icon."""
#     st.markdown(
#         f"""
#         <div style="
#             display: flex;
#             align-items: center;
#             justify-content: center;
#             width: 110px;
#             height: 110px;
#             border-radius: 50%;
#             background: linear-gradient(135deg, #00A3FF, #00CBA8);
#             box-shadow: 0 4px 20px rgba(0, 163, 255, 0.25);
#             margin: 15px auto;
#         ">
#             <span style="
#                 font-size: 70px;
#                 line-height: 1;
#                 text-shadow: 0 2px 4px rgba(0,0,0,0.25);
#             ">
#                 {emoji}
#             </span>
#         </div>
#         """,
#         unsafe_allow_html=True
#     )


# # --------------------------
# # TripCrew class with dynamic LLM fallback
# # --------------------------
# class TripCrew:
#     def __init__(self, origin, cities, date_range, interests):
#         self.cities = cities
#         self.origin = origin
#         self.interests = interests
#         self.date_range = f"{date_range[0].strftime('%Y-%m-%d')} to {date_range[1].strftime('%Y-%m-%d')}"
#         self.output_placeholder = st.empty()

#         # # Get API keys from secrets
#         # self.gemini_api_key = st.secrets["GEMINI_API_KEY"]
#         # self.openai_api_key = st.secrets["OPENAI_API_KEY"]
#         # self.browserless_api_key = st.secrets["BROWSERLESS_API_KEY"]
#         # self.serper_api_key = st.secrets["SERPER_API_KEY"]

#         # Load API keys (Render will inject via Environment Variables)
#         self.gemini_api_key = os.getenv("GEMINI_API_KEY", "")
#         self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
#         self.browserless_api_key = os.getenv("BROWSERLESS_API_KEY", "")
#         self.serper_api_key = os.getenv("SERPER_API_KEY", "")

#         # Initialize Gemini as the primary model
#         self.llm = self.create_llm("gemini")

#     def create_llm(self, provider="gemini"):
#         """Create LLM instance for Gemini or OpenAI."""
#         try:
#             if provider == "gemini":
#                 st.info("🧠 Using Gemini (Primary LLM)...")
#                 llm = LLM(model="gemini/gemini-2.5-flash", api_key=self.gemini_api_key)
#             elif provider == "openai":
#                 st.info("🪄 Switching to OpenAI (Fallback)...")
#                 llm = LLM(model="gpt-5-mini", api_key=self.openai_api_key)
#             else:
#                 raise ValueError("Invalid LLM provider")
#             return llm
#         except Exception as e:
#             st.error(f"Failed to initialize {provider}: {str(e)}")
#             raise

#     async def try_run_with_llm(self, llm):
#         """Run the crew process using a given LLM."""
#         agents = TripAgents(llm=llm)
#         tasks = TripTasks()

#         city_selector_agent = agents.city_selection_agent()
#         local_expert_agent = agents.local_expert()
#         travel_concierge_agent = agents.travel_concierge()

#         identify_task = tasks.identify_task(
#             city_selector_agent, self.origin, self.cities, self.interests, self.date_range,
#         )

#         gather_task = tasks.gather_task(
#             local_expert_agent, self.origin, self.interests, self.date_range,
#         )

#         plan_task = tasks.plan_task(
#             travel_concierge_agent, self.origin, self.interests, self.date_range,
#         )

#         crew = Crew(
#             agents=[city_selector_agent, local_expert_agent, travel_concierge_agent],
#             tasks=[identify_task, gather_task, plan_task],
#             verbose=True,
#         )

#         result = crew.kickoff()
#         return result

#     def run(self):
#         """Run trip planning with automatic Gemini → OpenAI fallback."""
#         try:
#             # --- Attempt 1: Gemini ---
#             result = asyncio.run(self.try_run_with_llm(self.llm))
#             self.output_placeholder.markdown(result)
#             return result
#         except Exception as gemini_error:
#             st.warning(f"⚠️ Gemini failed: {str(gemini_error)}")
#             traceback.print_exc()

#             # --- Attempt 2: Fallback to OpenAI ---
#             try:
#                 fallback_llm = self.create_llm("openai")
#                 result = asyncio.run(self.try_run_with_llm(fallback_llm))
#                 st.success("✅ Successfully continued with OpenAI fallback.")
#                 self.output_placeholder.markdown(result)
#                 return result
#             except Exception as openai_error:
#                 st.error(f"❌ Both Gemini and OpenAI failed.\n{openai_error}")
#                 traceback.print_exc()
#                 return None


# # ------------------------------------------------
# # PAGE CONFIGURATION
# # ------------------------------------------------
# st.set_page_config(
#     page_title="✈️ Agent-Powered Trip Planner",
#     page_icon="🌍",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )



# # ------------------------------------------------

# st.markdown("""
#     <style>
#     @import url('https://fonts.googleapis.com/css2?family=Inter:wght@100..900&display=swap');

#     /* 🌙 APP BACKGROUND + FONT */
#     .stApp {
#         background: linear-gradient(135deg, #0D0D0D, #1C1C1C, #2A2A2A);
#         color: #F0F0F0;
#         font-family: 'Inter', sans-serif;
#     }

#     /* 🏷️ TITLES */
#     .main-title {
#         font-size: 3rem;
#         font-weight: 800;
#         text-align: center;
#         background: linear-gradient(90deg, #00CBA8, #00A3FF);
#         -webkit-background-clip: text;
#         -webkit-text-fill-color: transparent;
#         text-shadow: 0px 0px 15px rgba(0, 163, 255, 0.4);
#         margin-bottom: 0.5rem;
#     }
#     .subtitle {
#         text-align: center;
#         color: #A0A0A0;
#         font-size: 1.2rem;
#         font-weight: 300;
#         margin-bottom: 3rem;
#     }

#     /* 📚 SIDEBAR */
#     section[data-testid="stSidebar"] {
#         background: rgba(18, 18, 18, 0.95);
#         border-right: 2px solid #00CBA8;
#         box-shadow: 5px 0 15px rgba(0, 0, 0, 0.5);
#         color: #EDEDED;
#     }
#     .sidebar-header {
#         font-size: 1.4rem;
#         font-weight: 700;
#         color: #00CBA8;
#         padding-top: 1rem;
#         padding-bottom: 1rem;
#         text-transform: uppercase;
#         letter-spacing: 1px;
#     }

#     /* 🎛️ SIDEBAR TOGGLE */
#     button[data-testid="baseButton-headerNoPadding"] {
#         color: #00FF99 !important;
#         background: rgba(0, 255, 153, 0.12) !important;
#         border: 1px solid #00FF99 !important;
#         border-radius: 50% !important;
#         width: 38px !important;
#         height: 38px !important;
#         display: flex !important;
#         align-items: center !important;
#         justify-content: center !important;
#         transition: all 0.3s ease-in-out !important;
#         z-index: 10000 !important;
#     }
#     button[data-testid="baseButton-headerNoPadding"]:hover,
#     button[data-testid="baseButton-headerNoPadding"]:active {
#         background: rgba(0, 255, 183, 0.25) !important;
#         transform: scale(1.2) !important;
#     }

#     /* ✏️ INPUT FIELDS */
#     .stTextInput input, .stDateInput input, .stTextArea textarea {
#         background-color: #242424 !important;
#         color: #F0F0F0 !important;
#         border-radius: 10px;
#         border: 1px solid #444444;
#         padding: 0.8rem 1rem;
#     }
#     .stTextInput input::placeholder, .stTextArea textarea::placeholder, .stDateInput input::placeholder {
#         color: #00CBA8 !important;
#         opacity: 0.8;
#     }
#     .stTextInput label, .stTextArea label, .stDateInput label {
#         color: #CCCCCC !important;
#         font-weight: 600;
#         margin-bottom: 0.25rem;
#     }

#     /* 🔘 BUTTONS - CENTERED & TAP-FRIENDLY */
#     div.stButton {
#         display: flex !important;
#         justify-content: center !important;
#         align-items: center !important;
#         width: 100% !important;
#         margin: 1rem 0;
#     }
#     div.stButton > button {
#         width: 80% !important;
#         max-width: 300px !important;
#         min-width: 180px !important;
#         background: linear-gradient(45deg, #00CBA8, #00A3FF) !important;
#         color: #FFFFFF !important;
#         border: none !important;
#         border-radius: 12px !important;
#         font-weight: 700 !important;
#         font-size: 1.1rem !important;
#         padding: 0.8rem !important;
#         text-align: center !important;
#         transition: all 0.3s ease !important;
#         cursor: pointer !important;
#         /* Replace hover shadow with active shadow for mobile tap */
#         box-shadow: 0 4px 15px rgba(0, 163, 255, 0.3) !important;
#     }
#     div.stButton > button:hover, 
#     div.stButton > button:focus,
#     div.stButton > button:active {
#         transform: translateY(-2px) scale(1.02);
#         background: linear-gradient(45deg, #00E0B8, #00B0FF) !important;
#         box-shadow: 0 6px 20px rgba(0, 163, 255, 0.5) !important;
#     }

#     /* 📦 EXPANDERS */
#     .stExpander {
#         background: rgba(255, 255, 255, 0.08) !important;
#         border-radius: 12px !important;
#         border: 1px solid rgba(0, 163, 255, 0.2) !important;
#         box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.3);
#         padding: 1rem;
#     }

#     /* ⚙️ FOOTER */
#     .footer {
#         text-align: center;
#         font-size: 0.85rem;
#         color: #888888;
#         padding-top: 2rem;
#     }

#     /* 🌐 MEDIA QUERIES - FULL RESPONSIVE */
#     @media (max-width: 768px) {
#         .main-title { font-size: 2.2rem; }
#         .subtitle { font-size: 1rem; }
#         div.stButton > button { width: 90% !important; font-size: 1rem !important; }
#     }
#     @media (max-width: 480px) {
#         .main-title { font-size: 1.8rem; }
#         .subtitle { font-size: 0.9rem; }
#         div.stButton > button { width: 95% !important; font-size: 0.95rem !important; }
#     }
#     </style>
#     """, unsafe_allow_html=True)



# # ------------------------------------------------
# # MAIN UI
# # ------------------------------------------------
# if __name__ == "__main__":
#     st.markdown("<div class='main-title'>⛩️💫 Infinity Odyssey Voyager ∇⩥</div>", unsafe_allow_html=True)
#     st.markdown("<div class='subtitle'>✨ Navigate Global Adventures with Futuristic AI Insight ⛢</div>", unsafe_allow_html=True)
#     st.divider()

#     today = datetime.datetime.now().date()
#     next_year = today.year + 1
#     jan_10_next_year = datetime.date(next_year, 1, 10)

#     # Sidebar Form
#     st.markdown("<div class='sidebar-header'>Plan Your Adventure</div>", unsafe_allow_html=True)
#     with st.form("trip_form"):
#         location = st.text_input("📍 Where are you currently located?", placeholder="Kuala Lumpur, Malaysia")
#         cities = st.text_input("🌆 Destination (City & Country)", placeholder="Rome, Italy")

#         # ✅ Two-Column Date Range Picker
#         col1, col2 = st.columns(2)
#         with col1:
#             start_date = st.date_input(
#                 "📅 Start Date",
#                 min_value=today,
#                 value=today,
#                 format="MM/DD/YYYY",
#                 key="start_date"
#             )
#         with col2:
#             end_date = st.date_input(
#                 "🏁 End Date",
#                 min_value=start_date,
#                 value=start_date + datetime.timedelta(days=6),
#                 format="MM/DD/YYYY",
#                 key="end_date"
#             )
#         # Combine into tuple for TripCrew
#         date_range = (start_date, end_date)

#         interests = st.text_area(
#             "🎯 High-level interests or trip details",
#             placeholder="2 adults who love swimming, dancing, hiking, and eating"
#         )

#         submitted = st.form_submit_button("✨ Generate My Trip Plan")

#     st.divider()

#     # ------------------------------------------------
#     # RUN TRIP PLANNER
#     # ------------------------------------------------
#     if "submitted" in locals() and submitted:
#         with st.status("🤖 **Agents at work...**", state="running", expanded=True) as status:
#             with st.container(height=500, border=False):
#                 sys.stdout = StreamToExpander(st)
#                 trip_crew = TripCrew(location, cities, date_range, interests)
#                 result = trip_crew.run()
#             status.update(label="✅ Trip Plan Ready!", state="complete", expanded=False)

#         if result:
#             st.subheader("🌍 Here’s your Dream Trip Plan", anchor=False, divider="rainbow")
#             st.markdown(result)
#             st.success("🌟 Trip plan generated successfully!", icon="✅")
#         else:
#             st.error("❌ Could not generate trip plan. Please check API keys or try again.")

#     # ------------------------------------------------
#     # FOOTER
#     # # ------------------------------------------------
#     # st.markdown("<div class='footer'>🚀 Powered by AI Agents | Designed with ❤️ using Streamlit & Inter Font</div>", unsafe_allow_html=True)

      

#     st.markdown("""
    
#     <div class="marquee-container">
#         <div class="marquee-content">
#             ✨ Crafting Futuristic Journeys with AI Precision 🌏 | 🛸 Autonomously Guided by AI ⧫✨
#         </div>
#     </div>

#     <style>
#     /* Container hides overflow */
#     .marquee-container {
#         overflow: hidden;
#         white-space: nowrap;
#         box-sizing: border-box;
#         width: 100%;
#         margin-top: 30px;
#         font-family: 'Inter', sans-serif;
#     }

#     /* Content scrolls continuously */
#     .marquee-content {
#         display: inline-block;
#         padding-left: 100%;
#         animation: marqueeAnim 12s linear infinite;
#         /* Gradient text */
#         background: linear-gradient(90deg, #FFD700, #00FFFF, #FF69B4, #7FFF00);
#         -webkit-background-clip: text;
#         -webkit-text-fill-color: transparent;
#         background-clip: text; /* Firefox support */
#         color: transparent;
#     }

#     /* Keyframes for continuous scroll */
#     @keyframes marqueeAnim {
#         0% { transform: translateX(0%); }
#         100% { transform: translateX(-50%); } /* Scrolls half content, because text repeated */
#     }

#     /* Responsive adjustments */
#     @media (max-width: 768px) {
#         .marquee-content {
#             font-size: 13px;
#             animation-duration: 15s;
#         }
#     }
#     @media (max-width: 480px) {
#         .marquee-content {
#             font-size: 12px;
#             animation-duration: 12s;
#         }
#     }
#     </style>
#     """, unsafe_allow_html=True)




# ager code work fine but it had some issue when give result it not give perfectly formatted result so I have modified some part of code to make it work perfectly

# it work perfectly fine now



import os
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

# ✅ Enables asyncio.run() inside Streamlit
nest_asyncio.apply()


# --------------------------
# Helper: display emoji
# --------------------------
def icon(emoji: str = "🌍"):
    """Shows a simple colorful agent-style emoji icon."""
    st.markdown(
        f"""
        <div style="
            display: flex;
            align-items: center;
            justify-content: center;
            width: 110px;
            height: 110px;
            border-radius: 50%;
            background: linear-gradient(135deg, #00A3FF, #00CBA8);
            box-shadow: 0 4px 20px rgba(0, 163, 255, 0.25);
            margin: 15px auto;
        ">
            <span style="
                font-size: 70px;
                line-height: 1;
                text-shadow: 0 2px 4px rgba(0,0,0,0.25);
            ">
                {emoji}
            </span>
        </div>
        """,
        unsafe_allow_html=True
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

        

        # Load API keys (Render will inject via Environment Variables)
        self.gemini_api_key = os.getenv("GEMINI_API_KEY", "")
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.browserless_api_key = os.getenv("BROWSERLESS_API_KEY", "")
        self.serper_api_key = os.getenv("SERPER_API_KEY", "")


        # Initialize Gemini as the primary model
        self.llm = self.create_llm("gemini")

    def create_llm(self, provider="gemini"):
        """Create LLM instance for Gemini or OpenAI."""
        try:
            if provider == "gemini":
                # st.info("🧠 Using Gemini (Primary LLM)...")
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
            city_selector_agent, self.origin, self.cities, self.interests, self.date_range,
        )

        gather_task = tasks.gather_task(
            local_expert_agent, self.origin, self.interests, self.date_range,
        )

        plan_task = tasks.plan_task(
            travel_concierge_agent, self.origin, self.interests, self.date_range,
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


# ------------------------------------------------
# PAGE CONFIGURATION
# ------------------------------------------------
st.set_page_config(
    page_title="✈️ Agent-Powered Trip Planner",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)



st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@100..900&display=swap');

    /* 🌙 APP BACKGROUND + FONT */
    .stApp {
        background: linear-gradient(135deg, #0D0D0D, #1C1C1C, #2A2A2A);
        color: #F0F0F0;
        font-family: 'Inter', sans-serif;
    }

    /* 🏷️ TITLES */
    .main-title {
        font-size: 3rem;
        font-weight: 800;
        text-align: center;
        background: linear-gradient(90deg, #00CBA8, #00A3FF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0px 0px 15px rgba(0, 163, 255, 0.4);
        margin-bottom: 0.5rem;
    }
    .subtitle {
        text-align: center;
        color: #A0A0A0;
        font-size: 1.2rem;
        font-weight: 300;
        margin-bottom: 3rem;
    }

    /* 📚 SIDEBAR */
    section[data-testid="stSidebar"] {
        background: rgba(18, 18, 18, 0.95);
        border-right: 2px solid #00CBA8;
        box-shadow: 5px 0 15px rgba(0, 0, 0, 0.5);
        color: #EDEDED;
    }
    .sidebar-header {
        font-size: 1.4rem;
        font-weight: 700;
        color: #00CBA8;
        padding-top: 1rem;
        padding-bottom: 1rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* 🎛️ SIDEBAR TOGGLE */
    button[data-testid="baseButton-headerNoPadding"] {
        color: #00FF99 !important;
        background: rgba(0, 255, 153, 0.12) !important;
        border: 1px solid #00FF99 !important;
        border-radius: 50% !important;
        width: 38px !important;
        height: 38px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        transition: all 0.3s ease-in-out !important;
        z-index: 10000 !important;
    }
    button[data-testid="baseButton-headerNoPadding"]:hover,
    button[data-testid="baseButton-headerNoPadding"]:active {
        background: rgba(0, 255, 183, 0.25) !important;
        transform: scale(1.2) !important;
    }

    /* ✏️ INPUT FIELDS */
    .stTextInput input, .stDateInput input, .stTextArea textarea {
        background-color: #242424 !important;
        color: #F0F0F0 !important;
        border-radius: 10px;
        border: 1px solid #444444;
        padding: 0.8rem 1rem;
    }
    .stTextInput input::placeholder, .stTextArea textarea::placeholder, .stDateInput input::placeholder {
        color: #00CBA8 !important;
        opacity: 0.8;
    }
    .stTextInput label, .stTextArea label, .stDateInput label {
        color: #CCCCCC !important;
        font-weight: 600;
        margin-bottom: 0.25rem;
    }

    /* 🔘 BUTTONS - CENTERED & TAP-FRIENDLY */
    div.stButton {
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        width: 100% !important;
        margin: 1rem 0;
    }
    div.stButton > button {
        width: 80% !important;
        max-width: 300px !important;
        min-width: 180px !important;
        background: linear-gradient(45deg, #00CBA8, #00A3FF) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
        padding: 0.8rem !important;
        text-align: center !important;
        transition: all 0.3s ease !important;
        cursor: pointer !important;
        /* Replace hover shadow with active shadow for mobile tap */
        box-shadow: 0 4px 15px rgba(0, 163, 255, 0.3) !important;
    }
    div.stButton > button:hover, 
    div.stButton > button:focus,
    div.stButton > button:active {
        transform: translateY(-2px) scale(1.02);
        background: linear-gradient(45deg, #00E0B8, #00B0FF) !important;
        box-shadow: 0 6px 20px rgba(0, 163, 255, 0.5) !important;
    }

    /* 📦 EXPANDERS */
    .stExpander {
        background: rgba(255, 255, 255, 0.08) !important;
        border-radius: 12px !important;
        border: 1px solid rgba(0, 163, 255, 0.2) !important;
        box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.3);
        padding: 1rem;
    }

    /* ⚙️ FOOTER */
    .footer {
        text-align: center;
        font-size: 0.85rem;
        color: #888888;
        padding-top: 2rem;
    }

    /* 🌐 MEDIA QUERIES - FULL RESPONSIVE */
    @media (max-width: 768px) {
        .main-title { font-size: 2.2rem; }
        .subtitle { font-size: 1rem; }
        div.stButton > button { width: 90% !important; font-size: 1rem !important; }
    }
    @media (max-width: 480px) {
        .main-title { font-size: 1.8rem; }
        .subtitle { font-size: 0.9rem; }
        div.stButton > button { width: 95% !important; font-size: 0.95rem !important; }
    }
    </style>
    """, unsafe_allow_html=True)



# ------------------------------------------------
# MAIN UI
# ------------------------------------------------
if __name__ == "__main__":
    st.markdown("<div class='main-title'>⛩️💫 Infinity Odyssey Voyager ∇⩥</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>✨ Navigate Global Adventures with Futuristic AI Insight ⛢</div>", unsafe_allow_html=True)
    st.divider()

    today = datetime.datetime.now().date()
    next_year = today.year + 1
    jan_10_next_year = datetime.date(next_year, 1, 10)

    # Sidebar Form
    st.markdown("<div class='sidebar-header'>Plan Your Adventure</div>", unsafe_allow_html=True)
    with st.form("trip_form"):
        location = st.text_input("📍 Where are you currently located?", placeholder="Kuala Lumpur, Malaysia")
        cities = st.text_input("🌆 Destination (City & Country)", placeholder="Rome, Italy")

        # ✅ Two-Column Date Range Picker
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "📅 Start Date",
                min_value=today,
                value=today,
                format="MM/DD/YYYY",
                key="start_date"
            )
        with col2:
            end_date = st.date_input(
                "🏁 End Date",
                min_value=start_date,
                value=start_date + datetime.timedelta(days=6),
                format="MM/DD/YYYY",
                key="end_date"
            )
        # Combine into tuple for TripCrew
        date_range = (start_date, end_date)

        interests = st.text_area(
            "🎯 High-level interests or trip details",
            placeholder="Visiting Paris for 7 days. We love swimming, dancing, hiking, trying local food, and exploring art museums. Looking for a mix of adventure and relaxation."
        )

        submitted = st.form_submit_button("✨ Generate My Trip Plan")

    st.divider()

    # ------------------------------------------------
    # RUN TRIP PLANNER
    # ------------------------------------------------
    if "submitted" in locals() and submitted:
        with st.status("🤖 **Agents at work...**", state="running", expanded=True) as status:
            with st.container(height=500, border=False):
                sys.stdout = StreamToExpander(st)
                trip_crew = TripCrew(location, cities, date_range, interests)
                result = trip_crew.run()
            status.update(label="✅ Trip Plan Ready!", state="complete", expanded=False)

        if result:
            st.subheader("🌍 Here’s your Dream Trip Plan", anchor=False, divider="rainbow")
            st.markdown(result)
            st.success("🌟 Trip plan generated successfully!", icon="✅")
        else:
            st.error("❌ Could not generate trip plan. Please check API keys or try again.")

    # ------------------------------------------------
    # FOOTER
    # ------------------------------------------------
    # st.markdown("<div class='footer'>✨ Curating Futuristic Expeditions with AI-Orchestrated Precision 🌏 |🛸 Guided by Autonomous AI Navigators ⧫✨</div>", unsafe_allow_html=True)

    
    st.markdown("""
    
    <div class="marquee-container">
        <div class="marquee-content">
            ✨ Crafting Futuristic Journeys with AI Precision 🌏 | 🛸 Autonomously Guided by AI ⧫✨
        </div>
    </div>

    <style>
    /* Container hides overflow */
    .marquee-container {
        overflow: hidden;
        white-space: nowrap;
        box-sizing: border-box;
        width: 100%;
        margin-top: 30px;
        font-family: 'Inter', sans-serif;
    }

    /* Content scrolls continuously */
    .marquee-content {
        display: inline-block;
        padding-left: 100%;
        animation: marqueeAnim 12s linear infinite;
        /* Gradient text */
        background: linear-gradient(90deg, #FFD700, #00FFFF, #FF69B4, #7FFF00);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text; /* Firefox support */
        color: transparent;
    }

    /* Keyframes for continuous scroll */
    @keyframes marqueeAnim {
        0% { transform: translateX(0%); }
        100% { transform: translateX(-50%); } /* Scrolls half content, because text repeated */
    }

    /* Responsive adjustments */
    @media (max-width: 768px) {
        .marquee-content {
            font-size: 13px;
            animation-duration: 15s;
        }
    }
    @media (max-width: 480px) {
        .marquee-content {
            font-size: 12px;
            animation-duration: 12s;
        }
    }
    </style>
    """, unsafe_allow_html=True)

    
