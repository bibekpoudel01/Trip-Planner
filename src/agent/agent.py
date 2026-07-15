import os
import logging
from chromadb import logger
from psycopg_pool import ConnectionPool
from psycopg.rows import dict_row
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.checkpoint.memory import InMemorySaver
from langchain_groq import ChatGroq
from langchain.agents import create_agent
from langchain.agents.middleware import AgentMiddleware
import logfire
from src.tools.places_info_search import (
    search_attractions,
    search_restaurants,
    search_activities,
    search_transportation,
    search_hotels,
    
)
from src.models.travel_models import TravelPlan
from src.tools.weather import get_weather_forecast
from src.tools.currency_conversion import convert_currency
from src.tools.final_recommendation import final_recommendation

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0,
    max_retries=5,
    timeout=60,
)


structuring_llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    max_retries=5,
    timeout=90,
)

TOOLS = [
    search_attractions,
    search_restaurants,
    search_activities,
    search_transportation,
    search_hotels,
    final_recommendation,
    convert_currency,
    get_weather_forecast
]


class TravelAgentMiddleware(AgentMiddleware):

    def before_agent(self, state, runtime):
        try:
            logfire.info(f"Agent Turn Started (History: {len(state.get('messages', []))} messages)")
            return None
        except Exception as e:
            raise Exception(f"Error in before_agent: {str(e)}") from e

    def after_model(self, state, runtime):
        try:
            return None
        except Exception as e:
            raise Exception(f"Error in after_model: {str(e)}") from e

    def after_agent(self, state, runtime):
        try:
            logfire.info("Agent turn completed")
            return None
        except Exception as e:
            raise Exception(f"Error in after_agent: {str(e)}") from e

COLLECTION_PROMPT = """
You are a travel research assistant. You have access to tools that each
search for a specific kind of information:
1. convert_currency        - convert amounts between currencies (use USD by default)
2. search_attractions       - attractions for a place
3. search_restaurants        - restaurants for a place and local foods to try
4. search_activities         - activities for a place
5. search_transportation      - trains, buses, taxis for a place
6. search_hotels             - hotels for a place
8. get_weather_forecast - day-wise weather forecast for the trip duration.                           
10.final_recommendation       - latest general travel recommendations for a destination
Use the tools to gather raw information relevant to the user's request.
Do NOT write a final report or draw conclusions - just collect data.
"""

def build_collector_agent():
    return create_agent(
        model=llm,
        tools=TOOLS,
        system_prompt=COLLECTION_PROMPT,
        middleware=[TravelAgentMiddleware()],
    )

def collector_agent(query: str):
    """Gathers raw travel information for `query` using the tool-enabled agent."""
    try:
        agent = build_collector_agent()
        response = agent.invoke({"messages": [{"role": "user", "content": query}]})
        return response
    except Exception as e:
        logfire.error("Error in collector_agent: {error}", error=str(e))
        return {"error": str(e)}


def title_generator(query: str) -> str:
    """Generates a short title for the travel report."""
    prompt = (
        f"Generate exactly ONE short, catchy title for a travel report based on this request: {query}\n"
        "Output ONLY the title text itself — no numbering, no options, no explanations, no quotation marks.\n"
        "Example format: Pokhara - Adventure Awaits: A 5-Day Itinerary for Nature Lovers"
    )
    try:
        response = llm.invoke(prompt)
        title = response.content.strip()
        if not title:
            raise ValueError("LLM returned empty title")
        return title
    except Exception as e:
        logfire.error("Error in title_generator: {error}", error=str(e))
        return "Travel Report (auto-generated title unavailable)"


REPORT_SYSTEM_PROMPT = """
You are a travel report writer. You will be given a title and a collection
of previously-gathered research (weather, hotels, attractions, restaurants with local food recommendations,
activities, transportation, currency conversion, and general
recommendations). Do not attempt to search for anything further - just
write the report using only the information provided to you.

Structure the report as follows:
0. Title: Use the title provided in the user message as the report's title.
1.. Weather Summary:
Provide the expected weather conditions during the trip duration.
Include temperature ranges, rain/cloud conditions, and practical packing advice.
2. Hotel recommendations- name and approximate price per night for each.
3. Day-by-day itinerary - for EACH day include:  activities, weather,
   attractions, restaurants with local food recommendations, transportation (if applicable) AND how to get between that day's locations.
4. Currency reference - convert the curerency from USD to destination currency and provide a reference for the traveler to use for budgeting. If no specific currency was requested, default to USD.
5. Final recommendations and warnings - give general recommendations, and 
   separately flag any safety warnings or travel advisories found in the research.
Note:Never Hallucinate. Be absolutely clear about what is based on the provided research data and what is a general travel recommendation. If data for a specific section is completely missing from the research, omit that section or state that no specific data was found instead of making it up.
    You must generate an itinerary for EXACTLY the number of days requested by the user.

"""



def get_database_url():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        return None
    if "sslmode=" not in database_url:
        separator = "&" if "?" in database_url else "?"
        database_url = f"{database_url}{separator}sslmode=require"
    return database_url


DATABASE_URL = get_database_url()

if DATABASE_URL:
    _pool = ConnectionPool(
        DATABASE_URL,
        min_size=1,
        max_size=10,
        kwargs={"autocommit": True, "row_factory": dict_row},
    )
    checkpointer = PostgresSaver(_pool)
    checkpointer.setup()
    logfire.info("Using Postgres checkpointer (pooled)")
else:
    checkpointer = InMemorySaver()
    logfire.warning(
        "DATABASE_URL not set. Using in-memory checkpointer; "
        "conversation state will reset on restart."
    )
def build_report_agent(cp):
    return create_agent(
        model=llm,
        tools=[],
        system_prompt=REPORT_SYSTEM_PROMPT,
        middleware=[TravelAgentMiddleware()],
        checkpointer=cp,
    )


report_agent = build_report_agent(checkpointer)



structured_model = structuring_llm.with_structured_output(TravelPlan)
logfire.info("Travel agent initialized (collector + tools-free report agent)")