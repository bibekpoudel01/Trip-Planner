from langchain.tools import tool
from langchain_tavily import TavilySearch
from src.config.config import *


def tavily_search_attractions(place: str) -> str:
    """Searches for attractions in the specified place using TavilySearch."""
    tavily_tool = TavilySearch(topic="general", include_answer="advanced")
    result = tavily_tool.invoke({"query": f"top attractive places and must-visit landmarks in and around {place}"})
    if isinstance(result, dict) and result.get("answer"):
        return str(result["answer"])
    return str(result)


def tavily_search_activity(place: str) -> str:
    """Searches for popular activities in the specified place using TavilySearch."""
    tavily_tool = TavilySearch(topic="general", include_answer="advanced")
    result = tavily_tool.invoke({"query": f"best things to do, outdoor activities, and experiences in and around {place}"})
    if isinstance(result, dict) and result.get("answer"):
        return str(result["answer"])
    return str(result)


def tavily_search_transportation(place: str) -> str:
    """Searches for available modes of transportation in the specified place using TavilySearch."""
    tavily_tool = TavilySearch(topic="general", include_answer="advanced")
    result = tavily_tool.invoke({"query": f"What are the different modes of transportation, taxi apps, and local transit available in {place}"})
    if isinstance(result, dict) and result.get("answer"):
        return str(result["answer"])
    return str(result)


def tavily_search_hotels(place: str) -> str:
    """Searches for available hotels in the specified place with prices and ratings."""
    tavily_tool = TavilySearch(topic="general", include_answer="advanced")
    # OPTIMIZED: Explicitly asking for prices and ratings so your Pydantic model gets populated
    query = f"what are the top 10 hotels in and around {place} including approximate price per night in USD and star or user ratings."
    result = tavily_tool.invoke({"query": query})
    if isinstance(result, dict) and result.get("answer"):
        return str(result["answer"])
    return str(result)


def tavily_search_restaurants(place: str) -> str:
    """Searches for available restaurants and local specialties in the specified place using TavilySearch."""
    tavily_tool = TavilySearch(topic="general", include_answer="advanced")
    query = f"what are the top 10 restaurants, eateries, and famous local foods or specialty dishes to try in and around {place}."
    result = tavily_tool.invoke({"query": query})
    if isinstance(result, dict) and result.get("answer"):
        return str(result["answer"])
    return str(result)



@tool
def search_restaurants(place: str) -> str:
    """
    Search for top-rated restaurants, cafes, and iconic local foods/dishes in a specific place.
    Use this tool to find both where to eat and what local specialties to order at those locations.
    """
    result = tavily_search_restaurants(place)
    return f"Following are the restaurants and iconic local food options for {place}:\n\n{result}"


@tool
def search_attractions(place: str) -> str:
    """
    Search for top tourist attractions, historical landmarks, and scenic points of interest in a place.
    """
    result = tavily_search_attractions(place)
    return f"Following are the attractions of {place}:\n\n{result}"


@tool
def search_activities(place: str) -> str:
    """
    Search for popular activities, tours, day trips, and things to do in a place.
    """
    result = tavily_search_activity(place)
    return f"Following are the activities in and around {place}:\n\n{result}"


@tool
def search_transportation(place: str) -> str:
    """
    Search for ways to get around a destination, including public transit, taxis, ridesharing, or car rentals.
    """
    result = tavily_search_transportation(place)
    return f"Following are the modes of transportation available in {place}:\n\n{result}"


@tool
def search_hotels(place: str) -> str:
    """
    Search for accommodations, hotels, and resorts in a place, including prices per night and ratings.
    """
    result = tavily_search_hotels(place)
    return f"Following are the hotels in and around {place}:\n\n{result}"