# from crewai import Agent, LLM
# import re
# import streamlit as st
# from langchain_core.language_models.chat_models import BaseChatModel
# from crewai import LLM
# from tools.browser_tools import BrowserTools
# from tools.calculator_tools import CalculatorTools
# from tools.search_tools import SearchTools
# import os


# class TripAgents():
#     def __init__(self, llm: BaseChatModel = None):
#         if llm is None:
#             try:
#                 # Primary: Gemini
#                 self.llm = LLM(model="gemini/gemini-2.0-flash")
                
#             except Exception as e:
#                 print(f"⚠️ Gemini model unavailable: {e}\nSwitching to GPT-4o fallback...")
#                 # Fallback: OpenAI GPT
#                 self.llm = LLM(model="gpt-5-mini", api_key=os.getenv("OPENAI_API_KEY"))
#                 print("✅ Fallback to GPT-4o successful")
#         else:
#             self.llm = llm

#         # Initialize tools once
#         self.search_tool = SearchTools()
#         self.browser_tool = BrowserTools()
#         self.calculator_tool = CalculatorTools()

#     def city_selection_agent(self):
#         return Agent(
#             role='City Selection Expert',
#             goal='Select the best city based on weather, season, and prices',
#             backstory='An expert in analyzing travel data to pick ideal destinations',
#             tools=[self.search_tool, self.browser_tool],
#             allow_delegation=False,
#             llm=self.llm,
#             verbose=True
#         )

#     def local_expert(self):
#         return Agent(
#             role='Local Expert at this city',
#             goal='Provide the BEST insights about the selected city',
#             backstory="""A knowledgeable local guide with extensive information
#         about the city, it's attractions and customs""",
#             tools=[self.search_tool, self.browser_tool],
#             allow_delegation=False,
#             llm=self.llm,
#             verbose=True
#         )

#     def travel_concierge(self):
#         return Agent(
#             role='Amazing Travel Concierge',
#             goal="""Create the most amazing travel itineraries with budget and 
#         packing suggestions for the city""",
#             backstory="""Specialist in travel planning and logistics with 
#         decades of experience""",
#             tools=[self.search_tool, self.browser_tool, self.calculator_tool],
#             allow_delegation=False,
#             llm=self.llm,
#             verbose=True
#         )


# class StreamToExpander:
#     def __init__(self, expander):
#         self.expander = expander
#         self.buffer = []
#         self.colors = ['red', 'green', 'blue', 'orange']
#         self.color_index = 0

#     def write(self, data):
#         # Filter out ANSI escape codes using a regular expression
#         cleaned_data = re.sub(r'\x1B\[[0-9;]*[mK]', '', data)

#         # Check if the data contains 'task' information
#         task_match_object = re.search(r'\"task\"\s*:\s*\"(.*?)\"', cleaned_data, re.IGNORECASE)
#         task_match_input = re.search(r'task\s*:\s*([^\n]*)', cleaned_data, re.IGNORECASE)
#         task_value = None
#         if task_match_object:
#             task_value = task_match_object.group(1)
#         elif task_match_input:
#             task_value = task_match_input.group(1).strip()

#         if task_value:
#             st.toast(":robot_face: " + task_value)

#         # Check if the text contains the specified phrase and apply color
#         if "Entering new CrewAgentExecutor chain" in cleaned_data:
#             self.color_index = (self.color_index + 1) % len(self.colors)
#             cleaned_data = cleaned_data.replace("Entering new CrewAgentExecutor chain", 
#                                               f":{self.colors[self.color_index]}[Entering new CrewAgentExecutor chain]")

#         if "City Selection Expert" in cleaned_data:
#             cleaned_data = cleaned_data.replace("City Selection Expert", 
#                                               f":{self.colors[self.color_index]}[City Selection Expert]")
#         if "Local Expert at this city" in cleaned_data:
#             cleaned_data = cleaned_data.replace("Local Expert at this city", 
#                                               f":{self.colors[self.color_index]}[Local Expert at this city]")
#         if "Amazing Travel Concierge" in cleaned_data:
#             cleaned_data = cleaned_data.replace("Amazing Travel Concierge", 
#                                               f":{self.colors[self.color_index]}[Amazing Travel Concierge]")
#         if "Finished chain." in cleaned_data:
#             cleaned_data = cleaned_data.replace("Finished chain.", 
#                                               f":{self.colors[self.color_index]}[Finished chain.]")

#         self.buffer.append(cleaned_data)
#         if "\n" in data:
#             self.expander.markdown(''.join(self.buffer), unsafe_allow_html=True)
#             self.buffer = []

#     def flush(self):
#         """Flush the buffer to the expander"""
#         if self.buffer:
#             self.expander.markdown(''.join(self.buffer), unsafe_allow_html=True)
#             self.buffer = []

#     def close(self):
#         """Close the stream"""
#         self.flush()


import re
import os
import logging
from crewai import Agent, LLM
from langchain_core.language_models.chat_models import BaseChatModel
from tools.browser_tools import BrowserTools
from tools.calculator_tools import CalculatorTools
from tools.search_tools import SearchTools

# ---------------------------
# 🔧 LOGGING CONFIGURATION
# ---------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("trip_agents.log"),
        logging.StreamHandler()
    ]
)

# ---------------------------
# 🧠 AGENTS CLASS
# ---------------------------
class TripAgents():
    def __init__(self, llm: BaseChatModel = None):
        if llm is None:
            try:
                # Primary: Gemini
                self.llm = LLM(model="gemini/gemini-2.0-flash")
                logging.info("✅ Successfully initialized Gemini model (gemini-2.0-flash)")
            except Exception as e:
                print(f"⚠️ Gemini model unavailable: {e}\nSwitching to GPT fallback...")
                logging.warning(f"Gemini model unavailable: {e}. Switching to GPT fallback...")

                # Fallback: OpenAI GPT
                self.llm = LLM(model="gpt-5-mini", api_key=os.getenv("OPENAI_API_KEY"))
                print("✅ Fallback to GPT-5-mini successful")
                logging.info("✅ Fallback to GPT-5-mini successful")
        else:
            self.llm = llm
            logging.info("Using provided LLM instance")

        # Initialize tools
        self.search_tool = SearchTools()
        self.browser_tool = BrowserTools()
        self.calculator_tool = CalculatorTools()
        logging.info("✅ Tools initialized successfully")

    def city_selection_agent(self):
        logging.info("Creating City Selection Expert agent...")
        return Agent(
            role='City Selection Expert',
            goal='Select the best city based on weather, season, and prices',
            backstory='An expert in analyzing travel data to pick ideal destinations',
            tools=[self.search_tool, self.browser_tool],
            allow_delegation=False,
            llm=self.llm,
            verbose=True
        )

    def local_expert(self):
        logging.info("Creating Local Expert agent...")
        return Agent(
            role='Local Expert at this city',
            goal='Provide the BEST insights about the selected city',
            backstory="""A knowledgeable local guide with extensive information
        about the city, its attractions and customs""",
            tools=[self.search_tool, self.browser_tool],
            allow_delegation=False,
            llm=self.llm,
            verbose=True
        )

    def travel_concierge(self):
        logging.info("Creating Amazing Travel Concierge agent...")
        return Agent(
            role='Amazing Travel Concierge',
            goal="""Create the most amazing travel itineraries with budget and 
        packing suggestions for the city""",
            backstory="""Specialist in travel planning and logistics with 
        decades of experience""",
            tools=[self.search_tool, self.browser_tool, self.calculator_tool],
            allow_delegation=False,
            llm=self.llm,
            verbose=True
        )


# ---------------------------
# 🧾 STREAM (LOG) OUTPUT HANDLER (NO STREAMLIT)
# ---------------------------
class StreamToConsole():
    def __init__(self):
        self.buffer = []
        self.colors = ['\033[91m', '\033[92m', '\033[94m', '\033[93m']  # red, green, blue, yellow
        self.color_index = 0
        self.reset_color = '\033[0m'
        logging.info("StreamToConsole initialized")

    def write(self, data):
        # Remove ANSI codes from input text (if any)
        cleaned_data = re.sub(r'\x1B\[[0-9;]*[mK]', '', data)

        # Extract potential task text
        task_match_object = re.search(r'\"task\"\s*:\s*\"(.*?)\"', cleaned_data, re.IGNORECASE)
        task_match_input = re.search(r'task\s*:\s*([^\n]*)', cleaned_data, re.IGNORECASE)
        task_value = None

        if task_match_object:
            task_value = task_match_object.group(1)
        elif task_match_input:
            task_value = task_match_input.group(1).strip()

        # Show task message
        if task_value:
            message = f"🤖 Task Detected: {task_value}"
            print(message)
            logging.info(message)

        # Highlight major sections with color
        if "Entering new CrewAgentExecutor chain" in cleaned_data:
            self.color_index = (self.color_index + 1) % len(self.colors)
            colored = f"{self.colors[self.color_index]}Entering new CrewAgentExecutor chain{self.reset_color}"
            cleaned_data = cleaned_data.replace("Entering new CrewAgentExecutor chain", colored)
            logging.info("➡️ Entering new CrewAgentExecutor chain detected")

        if "City Selection Expert" in cleaned_data:
            colored = f"{self.colors[self.color_index]}City Selection Expert{self.reset_color}"
            cleaned_data = cleaned_data.replace("City Selection Expert", colored)
            logging.info("👩‍💼 City Selection Expert activity detected")

        if "Local Expert at this city" in cleaned_data:
            colored = f"{self.colors[self.color_index]}Local Expert at this city{self.reset_color}"
            cleaned_data = cleaned_data.replace("Local Expert at this city", colored)
            logging.info("🧭 Local Expert activity detected")

        if "Amazing Travel Concierge" in cleaned_data:
            colored = f"{self.colors[self.color_index]}Amazing Travel Concierge{self.reset_color}"
            cleaned_data = cleaned_data.replace("Amazing Travel Concierge", colored)
            logging.info("🎒 Amazing Travel Concierge activity detected")

        if "Finished chain." in cleaned_data:
            colored = f"{self.colors[self.color_index]}Finished chain.{self.reset_color}"
            cleaned_data = cleaned_data.replace("Finished chain.", colored)
            logging.info("🏁 Finished chain detected")

        # Print formatted data
        self.buffer.append(cleaned_data)
        if "\n" in data:
            output = ''.join(self.buffer)
            print(output, end='')
            self.buffer = []

    def flush(self):
        """Flush remaining data to console"""
        if self.buffer:
            print(''.join(self.buffer))
            logging.info("🔄 Flushed remaining buffer to console")
            self.buffer = []

    def close(self):
        """Close stream"""
        self.flush()
        logging.info("🧹 Stream closed and flushed")


# Example usage (for testing)
if __name__ == "__main__":
    trip = TripAgents()
    stream = StreamToConsole()
    test_data = """
    {"task": "Selecting best city for travel"}
    Entering new CrewAgentExecutor chain
    City Selection Expert analyzing data...
    Finished chain.
    """
    stream.write(test_data)
    stream.close()
