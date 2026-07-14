from typing import List, Dict
from langchain_core.tools import tool
from langchain_community.utilities import GoogleSerperAPIWrapper
import os
from src.config.config import *

@tool
def final_recommendation(query: str) -> List[Dict]:
    """
     Search the web for up-to-date information related to a destination,
    including safety warnings, travel advisories, and current alerts.

    Args:
        query: A search query describing the destination and information
            to search for.

    Returns:
        A list of relevant search results containing:
        - title
        - link
        - snippet
    """

    api_key = os.getenv("SERPER_API_KEY")

    if not api_key:
        return [{"error": "SERPER_API_KEY not configured"}]

    try:
        serper = GoogleSerperAPIWrapper(serper_api_key=api_key)
        result = serper.run(query)
        return result

    except Exception as e:
        return [{"error": str(e)}]