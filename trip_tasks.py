from crewai import Task
from textwrap import dedent
from datetime import date
import streamlit as st

class TripTasks():
    def __validate_inputs(self, origin, cities, interests, date_range):
        if not origin or not cities or not interests or not date_range:
            raise ValueError("All input parameters must be provided")
        return True

    def identify_task(self, agent, origin, cities, interests, range):
        self.__validate_inputs(origin, cities, interests, range)

    
        return Task(
            description=dedent(f"""
                Analyze and select the **best city** for the upcoming trip from the given options,
                using a **comprehensive multi-factor evaluation**. Your role is to act as a 
                professional travel consultant, comparing all candidate cities on the following criteria:

                1. **Weather & Seasonal Conditions**
                - Current weather forecast for the exact travel dates: {range}.
                - Typical seasonal climate patterns (temperature, rainfall, humidity).
                - Suitability of weather for the traveler’s interests: {interests}.
                - Any extreme conditions or advisories (storms, heatwaves, monsoons, etc.).

                2. **Cultural & Seasonal Events**
                - Major festivals, concerts, exhibitions, or local holidays during the trip period.
                - Impact on the trip (higher energy, cultural immersion, or overcrowding, price spikes).
                - How these events enhance or limit the traveler’s experience.

                3. **Travel Costs**
                - Actual flight costs from {origin} to each city (economy-class average).
                - Accommodation averages (3–4 star hotels or equivalent per night).
                - Local transportation (metro passes, taxis, rideshare costs).
                - Meal costs (average daily spend for breakfast, lunch, and dinner).
                - Attraction entry fees and extras.
                - Total estimated trip budget for each option.

                4. **Traveler Interests & Attractions**
                - Match the traveler’s interests {interests} to real attractions and activities.
                - Identify must-see landmarks, museums, outdoor spaces, or hidden gems.
                - Explain why each recommended place is relevant and worth visiting.

                5. **Accessibility & Practical Factors**
                - Visa requirements or restrictions (if applicable).
                - Safety considerations (crime rate, scams, health advisories).
                - Language/cultural barriers and ease of navigation for visitors.
                - Transportation convenience (public transport, walking-friendliness, airports).

                ---
                🔎 **Final Deliverable**

                Your final answer must be a **detailed and structured travel report** recommending
                ONE city as the best option. The report must include:

                - 🏙️ **Chosen City & Justification**: Explain why this city stands out.
                - 🌦️ **Weather Forecast**: Daily outlook with implications for activities.
                - ✈️ **Flight Costs**: At least 2 actual sample flight options with prices and duration.
                - 🏨 **Accommodation Options**: Specific hotels (with prices, location, and reasoning).
                - 🎭 **Events & Seasonal Highlights**: What’s happening in the city during {range}.
                - 🗺️ **Attractions & Activities**: Specific recommendations matched to interests.
                - 💰 **Budget Breakdown**: Estimated total cost (flights, hotels, food, transport, attractions).
                - ⚠️ **Risks & Considerations**: Any potential downsides or travel advisories.
                - ✅ **Final Recommendation**: A clear conclusion on why this city provides
                the BEST overall experience for this trip.

                {self.__tip_section()}

                Traveling From: {origin}  
                City Options: {cities}  
                Trip Date: {range}  
                Traveler Interests: {interests}
            """),
            expected_output=(
                "A professional travel report recommending the best city, "
                "with actual flight costs, daily weather forecast, cultural events, "
                "specific attractions, hotel options, estimated budget, and reasoning."
            ),
            agent=agent,
            output_key="chosen_city"  # <-- Add this
        )

    def gather_task(self, agent, origin, interests, range):
        


        return Task(
            description=dedent(f"""
                As a **local expert** on this city, create an **in-depth, insider-style travel guide**
                designed to help a visitor have THE BEST possible trip during {range}.
                The guide should go beyond generic tourist information, providing **local insights,
                hidden gems, cultural etiquette, and practical travel advice**.

                ### Scope of the Guide

                1. **City Overview**
                - A short introduction capturing the city's character and vibe.
                - Why this city is special and worth visiting.

                2. **Weather & Seasonal Insights**
                - Weather forecast during the travel period ({range}).
                - Seasonal climate expectations (temperature, rainfall, humidity).
                - Best clothing recommendations and packing tips.

                3. **Attractions & Activities**
                - Must-visit landmarks and world-famous sites.
                - Cultural hotspots (museums, theaters, galleries, historic districts).
                - Hidden gems only locals know (cafés, neighborhoods, secret spots).
                - Daily activity recommendations tailored to traveler interests: {interests}.
                - Suggested morning, afternoon, and evening activities for balance.

                4. **Food & Dining**
                - Iconic local dishes to try (street food + fine dining).
                - Specific restaurants, cafés, or food markets with insider reasoning
                    (authenticity, atmosphere, popularity among locals).
                - Unique food experiences (cooking classes, night markets, food tours).

                5. **Events & Festivals**
                - Cultural or seasonal events happening during the trip dates.
                - Why these events are meaningful and how they enhance the experience.

                6. **Local Customs & Culture**
                - Essential etiquette, dos and don’ts (greetings, tipping, dress codes).
                - Key cultural values and traditions travelers should respect.
                - Useful local phrases or expressions.

                7. **Neighborhoods & Areas to Explore**
                - Best districts for history, nightlife, shopping, and relaxation.
                - Recommendations for safe and authentic experiences.

                8. **Transportation & Navigation**
                - How to get around (public transport, taxis, walking, bike rentals).
                - Insider tips to save money and avoid common tourist pitfalls.

                9. **Costs & Budget**
                - High-level cost overview (average hotel rates, daily food costs,
                    transport passes, attraction entry fees).
                - Options for both budget-friendly and premium travelers.

                10. **Safety & Practical Tips**
                    - Safety notes (scams, common issues, areas to avoid).
                    - Health tips, emergency numbers, and essential apps.
                    - Travel hacks to maximize the trip.

                ---
                🔎 **Final Deliverable**

                Your final output must be a **comprehensive city guide** written in a clear,
                engaging style. It should feel like advice from a well-connected local friend
                who knows all the best spots and how to navigate the city like a pro.

                The guide should include:
                - 🌆 City introduction and vibe
                - 🌦️ Weather and packing guidance
                - 🗺️ Attractions (famous + hidden gems)
                - 🍽️ Food and dining highlights
                - 🎭 Seasonal events and festivals
                - 🙌 Local customs and etiquette
                - 🏙️ Neighborhood breakdown
                - 🚇 Transportation tips
                - 💰 High-level costs and budgeting advice
                - ⚠️ Safety and insider tips

                {self.__tip_section()}

                Trip Date: {range}  
                Traveling from: {origin}  
                Traveler Interests: {interests}
            """),
            expected_output=(
                "A professional city guide with cultural insights, hidden gems, food recommendations, "
                "events, transportation, budgeting, weather, and practical travel tips."
            ),
            agent=agent,
            depends_on=["chosen_city"],  # <-- link dependency
            output_key="city_guide"
        )

    def plan_task(self, agent, origin, interests, range):


        return Task(
            description=dedent(f"""
                Expand this guide into a **full travel itinerary** for the selected
                time period ({range}), building a **day-by-day trip plan** that covers
                every major detail a traveler would need. This itinerary must include:

                1. **Daily Schedule**
                - Morning, afternoon, and evening activities.
                - Actual attractions, museums, neighborhoods, and hidden gems.
                - Logical sequencing (minimize travel time between stops).
                - Suggested downtime or relaxation periods.

                2. **Weather Forecast Integration**
                - Anticipated weather for each day.
                - How the weather impacts activities (e.g., indoor vs outdoor).
                - Contingency options if weather shifts unexpectedly.

                3. **Food & Dining**
                - Specific restaurants, cafés, and street food spots.
                - A mix of local favorites, iconic must-tries, and hidden gems.
                - Justification for each pick (authentic cuisine, cultural value, ratings).

                4. **Accommodation**
                - Recommended actual hotels, boutique stays, or Airbnbs.
                - Location reasoning (proximity to attractions, safety, transport).
                - Approximate nightly rate.

                5. **Packing & Clothing Suggestions**
                - Daily clothing suggestions based on weather forecast.
                - Essential items (jackets, umbrellas, sunscreen, power adapters).
                - Activity-specific gear (hiking shoes, swimwear, evening outfits).

                6. **Budget Breakdown**
                - Flights from {origin} (actual price range).
                - Accommodation costs (total for the stay).
                - Daily activity/entrance fees.
                - Food and drinks (average per meal).
                - Local transportation (metro, taxi, rideshare, passes).
                - Souvenirs & miscellaneous.
                - Final estimated total trip budget.

                7. **Practical Travel Logistics**
                - Airport arrival & transfer details (how to get to the hotel).
                - Local transportation recommendations (metro cards, bus passes, bikes).
                - Safety notes (pickpockets, scams, neighborhoods to avoid).
                - Cultural etiquette (tipping, dress codes, polite customs).
                - Language tips (useful phrases or apps).

                8. **Special Highlights**
                - At least one unique or off-the-beaten-path experience per day.
                - Why each attraction, restaurant, or activity is worth including.
                - Seasonal or cultural events happening during {range}.

                Your final answer MUST be a **fully fleshed-out travel plan** formatted
                in **Markdown**, with sections like:

                - 🛬 Arrival & Departure logistics  
                - 📅 Day-by-Day Itinerary (with weather, activities, meals, and costs)  
                - 🏨 Accommodation details  
                - 🍽️ Restaurant & food guide  
                - 🎒 Packing checklist  
                - 💰 Budget breakdown  
                - ⚠️ Travel tips & safety notes  

                This should read like a **professional travel agency itinerary**,
                ensuring that the traveler enjoys THE BEST TRIP EVER.

                {self.__tip_section()}

                Trip Date: {range}  
                Traveling from: {origin}  
                Traveler Interests: {interests}
            """),
            expected_output=(
                "A complete multi-day travel plan (e.g., 7-day), formatted in Markdown, "
                "with a per-day schedule, weather forecasts, actual attractions, restaurants, "
                "hotels, packing list, safety notes, and a detailed budget breakdown."
            ),
            agent=agent,
            depends_on=["chosen_city", "city_guide"],  # <-- combine previous results
            output_key="final_itinerary"
        )

    def __tip_section(self):
        return "If you do your BEST WORK, I'll tip you $100 and grant you any wish you want!"
