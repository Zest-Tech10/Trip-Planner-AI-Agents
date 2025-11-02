from crewai import Task
from textwrap import dedent

class TripTasks():
    def __validate_inputs(self, origin, cities, interests, date_range):
        if not origin or not cities or not interests or not date_range:
            raise ValueError("All input parameters must be provided")
        return True

    # 🧭 STEP 1: Identify the best city
    def identify_task(self, agent, origin, cities, interests, range):
        self.__validate_inputs(origin, cities, interests, range)

        return Task(
            description=dedent(f"""
                🧠 **Role**: You are an expert *AI Travel Advisor*.

                ✈️ **Goal**: From the given city list {cities}, 
                choose the **most suitable destination** for a trip 
                starting from **{origin}** during **{range}**, 
                perfectly aligned with the traveler’s interest in **{interests}**.

                💡 **Consider these key factors**:
                1. Weather suitability for {interests}
                2. Major attractions that match {interests}
                3. Estimated travel cost (flight + 3-night hotel average)

                🗂️ **Your Output Must Include**:
                - Highlighted destination (with a clear reason for choice)
                - Top 3 attractions
                - Estimated overall trip cost (USD or local currency)

                {self.__tip_section()}
            """),
            expected_output="A short, formatted travel report recommending one city with top attractions and estimated total cost.",
            agent=agent,
            output_key="chosen_city"
        )

    # 🏙️ STEP 2: Create a City Guide
    def gather_task(self, agent, origin, interests, range):
        return Task(
            description=dedent(f"""
                🌍 **Role**: You are a *Travel Insights Curator*.

                🎯 **Goal**: Create a **concise city guide** for the selected city (‘chosen_city’) 
                that gives travelers a sense of excitement and readiness.

                🗺️ **Include These Sections**:
                - ✨ **City Overview**: 2–3 engaging sentences that capture the city’s vibe.
                - 🏛️ **Top 5 Attractions**: Each with a short reason why it’s worth visiting.
                - 🍽️ **Top 3 Food Experiences**: Must-try local dishes or restaurants.
                - 🎉 **Seasonal Highlights**: Events, festivals, or activities during **{range}**.

                Keep it **clear, useful, and traveler-friendly** — like a professional brochure.

                {self.__tip_section()}
            """),
            expected_output="A practical, engaging city guide with overview, attractions, food, and events.",
            agent=agent,
            depends_on=["chosen_city"],
            output_key="city_guide"
        )

    # 🗓️ STEP 3: Design the Itinerary
    def plan_task(self, agent, origin, interests, range):
        return Task(
            description=dedent(f"""
                🧭 **Role**: You are a *Travel Experience Designer*.

                🎯 **Goal**: Using the ‘city_guide’, create a **3–5 day personalized itinerary** 
                for a traveler departing from **{origin}** during **{range}**, 
                focused on **{interests}**.

                📋 **Itinerary Structure**:
                - 🕰️ **Daily Activities** (morning, afternoon, evening)
                - 🍴 **Recommended Restaurants** (1–2 per day)
                - 🏨 **Accommodation Suggestion**
                - 💰 **Estimated Daily Cost**

                💵 **Budget Breakdown**:
                - Flights ✈️
                - Hotels 🏨
                - Meals 🍜
                - Local Transport 🚗
                - Attractions 🎟️
                - Total 💵

                🆓 **Free Activities**: Include scenic or cultural spots with no entry fee.  
                💸 **Paid Activities**: List approximate costs.  
                🛡️ **Travel Tips & Safety Notes**: Health, customs, and smart local behavior.

                Format it neatly with clear titles and short actionable bullet points.  
                Focus on making it *feel like a real trip plan.*

                {self.__tip_section()}
            """),
            expected_output="A well-formatted 3–5 day travel itinerary with activities, food, accommodation, budget, and safety tips.",
            agent=agent,
            depends_on=["chosen_city", "city_guide"],
            output_key="final_itinerary"
        )

    # ✨ Motivational Tip Section
    def __tip_section(self):
        return dedent("""
            🚀 **Tip**: Make the output visually clear — use section titles, emojis, and bullet points.  
            Always ensure readability, excitement, and travel clarity.  
            This plan should inspire the traveler to pack their bags right away!
        """)
# ============================================================