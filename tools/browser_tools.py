# import os
# import json
# import requests
# import streamlit as st
# from crewai.tools import BaseTool
# from pydantic import BaseModel, Field
# from unstructured.partition.html import partition_html
# from crewai import Agent, Task
# from langchain_openai import ChatOpenAI

# from crewai import LLM

# class WebsiteInput(BaseModel):
#     website: str = Field(..., description="The website URL to scrape")

# class BrowserTools(BaseTool):
#     name: str = "Scrape website content"
#     description: str = "Useful to scrape and summarize a website content"
#     args_schema: type[BaseModel] = WebsiteInput

#     def _run(self, website: str) -> str:
#         try:
#             # url = f"https://chrome.browserless.io/content?token={st.secrets['BROWSERLESS_API_KEY']}"
#             url = f"https://chrome.browserless.io/content?token={os.getenv('BROWSERLESS_API_KEY')}"
#             payload = json.dumps({"url": website})
#             headers = {'cache-control': 'no-cache', 'content-type': 'application/json'}
#             response = requests.request("POST", url, headers=headers, data=payload)
            
#             if response.status_code != 200:
#                 return f"Error: Failed to fetch website content. Status code: {response.status_code}"
            
#             elements = partition_html(text=response.text)
#             content = "\n\n".join([str(el) for el in elements])
#             content = [content[i:i + 8000] for i in range(0, len(content), 8000)]
#             summaries = []
            
#             # ----------------------------------------------------------------------
#             # STEP 2: Try Gemini first, fallback to GPT if Gemini fails
#             # ----------------------------------------------------------------------
#             llm = None
#             try:
#                 llm = LLM(model="gemini/gemini-2.0-flash")
#                 # Optional quick test call to verify Gemini works
#             except Exception as e:
#                 print(f"⚠️ Gemini failed: {e}\nSwitching to GPT-4o-mini fallback...")
#                 llm = LLM(
#                     model="gpt-5-mini",
#                     api_key=os.getenv("OPENAI_API_KEY")
#                 )
#                 print("✅ Fallback to GPT-5-mini successful")
            
#             for chunk in content:
#                 agent = Agent(
#                     role='Principal Researcher',
#                     goal='Do amazing researches and summaries based on the content you are working with',
#                     backstory="You're a Principal Researcher at a big company and you need to do a research about a given topic.",
#                     allow_delegation=False,
#                     llm=llm
#                 )
#                 task = Task(
#                     description=f'Analyze and summarize the content below, make sure to include the most relevant information in the summary, return only the summary nothing else.\n\nCONTENT\n----------\n{chunk}',
#                     agent=agent
#                 )
#                 summary = task.execute()
#                 summaries.append(summary)
#             return "\n\n".join(summaries)
#         except Exception as e:
#             return f"Error while processing website: {str(e)}"

#     async def _arun(self, website: str) -> str:
#         raise NotImplementedError("Async not implemented")


import os
import json
import requests
import logging
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from unstructured.partition.html import partition_html
from crewai import Agent, Task, LLM

# ---------------------------
# 🔧 LOGGING CONFIGURATION
# ---------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("browser_tools.log"),
        logging.StreamHandler()
    ]
)

# ---------------------------
# 🧠 INPUT SCHEMA
# ---------------------------
class WebsiteInput(BaseModel):
    website: str = Field(..., description="The website URL to scrape")

# ---------------------------
# 🌐 BROWSER TOOLS CLASS
# ---------------------------
class BrowserTools(BaseTool):
    name: str = "Scrape website content"
    description: str = "Useful to scrape and summarize website content"
    args_schema: type[BaseModel] = WebsiteInput

    def _run(self, website: str) -> str:
        try:
            logging.info(f"🌐 Starting scrape for: {website}")
            
            # URL for Browserless API
            api_key = os.getenv("BROWSERLESS_API_KEY")
            if not api_key:
                logging.error("❌ Missing BROWSERLESS_API_KEY environment variable.")
                return "Error: Missing Browserless API key."

            url = f"https://chrome.browserless.io/content?token={api_key}"
            payload = json.dumps({"url": website})
            headers = {'cache-control': 'no-cache', 'content-type': 'application/json'}

            # Make request
            response = requests.post(url, headers=headers, data=payload)

            if response.status_code != 200:
                error_msg = f"Error: Failed to fetch website content. Status code: {response.status_code}"
                logging.error(error_msg)
                return error_msg

            # Extract content from HTML
            elements = partition_html(text=response.text)
            content = "\n\n".join([str(el) for el in elements])
            logging.info(f"✅ Successfully scraped {len(content)} characters from {website}")

            # Split into chunks for summarization
            content_chunks = [content[i:i + 8000] for i in range(0, len(content), 8000)]
            summaries = []

            # ----------------------------------------------------------------------
            # STEP 2: Try Gemini first, fallback to GPT if Gemini fails
            # ----------------------------------------------------------------------
            llm = None
            try:
                logging.info("🔹 Attempting to initialize Gemini model (gemini-2.0-flash)")
                llm = LLM(model="gemini/gemini-2.0-flash")
                # logging.info("✅ Gemini model initialized successfully")
            except Exception as e:
                logging.warning(f"⚠️ Gemini initialization failed: {e}")
                logging.info("Switching to GPT-5-mini fallback...")
                llm = LLM(model="gpt-5-mini", api_key=os.getenv("OPENAI_API_KEY"))
                logging.info("✅ Fallback to GPT-5-mini successful")

            # ----------------------------------------------------------------------
            # STEP 3: Summarize each chunk
            # ----------------------------------------------------------------------
            for i, chunk in enumerate(content_chunks, start=1):
                logging.info(f"🧠 Summarizing chunk {i}/{len(content_chunks)}...")

                agent = Agent(
                    role='Principal Researcher',
                    goal='Produce high-quality summaries of research materials.',
                    backstory="You are an experienced research analyst who extracts and summarizes important insights from text.",
                    allow_delegation=False,
                    llm=llm
                )

                task_description = (
                    f"Analyze and summarize the content below. Include only the most relevant information.\n\n"
                    f"CONTENT\n----------\n{chunk}"
                )
                task = Task(description=task_description, agent=agent)

                try:
                    summary = task.execute()
                    summaries.append(summary)
                    logging.info(f"✅ Chunk {i} summarized successfully")
                except Exception as e:
                    error_msg = f"❌ Failed to summarize chunk {i}: {e}"
                    logging.error(error_msg)
                    summaries.append(error_msg)

            # Join all summaries together
            full_summary = "\n\n".join(summaries)
            logging.info("🏁 Website summarization complete.")
            return full_summary

        except Exception as e:
            logging.exception(f"❌ Error while processing website: {e}")
            return f"Error while processing website: {str(e)}"

    async def _arun(self, website: str) -> str:
        raise NotImplementedError("Async not implemented yet.")
