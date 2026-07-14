import json
import uuid
from datetime import datetime

import logfire
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from src.agent.agent import (
    collector_agent,
    report_agent,
    structured_model,
    title_generator,
)
from src.utils.logger import get_logger

logger = get_logger(__name__)
MAX_TOOL_OUTPUT_CHARS = 1500


def _safe_truncate(content: str, limit: int = MAX_TOOL_OUTPUT_CHARS) -> str:
    """Truncate tool output while attempting to preserve valid JSON."""
    if len(content) <= limit:
        return content

    try:
        parsed = json.loads(content)
        compact = json.dumps(parsed, separators=(",", ":"))
        if len(compact) <= limit:
            return compact
    except (json.JSONDecodeError, TypeError):
        pass

    logger.warning(
        "Tool output truncated: %d chars -> %d chars", len(content), limit
    )
    return content[:limit] + " ...[TRUNCATED]"

class TravelPlanner:
    def __init__(self):
        logger.info("Travel Planner initialized")

    @logfire.instrument("create_itinerary")
    def create_itinerary(
        self,
        city: str,
        days: int,
        interests: list[str],
        style: str,
        pace: str,
        month: str | None = None,
        extra_info: str | None = None,
        thread_id: str | None = None,
        currency: str | None = None,
    ):
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            thread_id = thread_id or str(uuid.uuid4())

            collect_query = f"""
                      Research a trip to {city} for EXACTLY {days} day(s). Do not gather information
        for more or fewer than {days} day(s).

        Current date: {today}

                    
                    Interests: {", ".join(interests)}
                    Travel style: {style}
                    Pace: {pace}
                    Month: {month or "Any"}
                    Preferred currency: {currency or "USD"}
                    Extra info: {extra_info or "None"}

                    Gather weather, hotels, attractions, restaurants with local food recommendations, activities,
                    transportation,final recommendations along with currency information for conversion this trip.
                    """

            collected = collector_agent(collect_query)

            if isinstance(collected, dict) and "error" in collected:
                raise RuntimeError(f"Collector agent failed: {collected['error']}")

            collected_messages = collected.get("messages", [])
            tool_calls = []
            retrieval_context = []

            for msg in collected_messages:
                if isinstance(msg, AIMessage) and getattr(msg, "tool_calls", None):
                    for tc in msg.tool_calls:
                        tool_calls.append(
                            {
                                "name": tc["name"],
                                "args": tc["args"],
                            }
                        )
                        logger.info(
                            "Tool Used: %s | Args: %s",
                            tc["name"],
                            tc["args"],
                        )
                elif isinstance(msg, ToolMessage):
                    tool_name = getattr(msg, "name", "unknown_tool")
                    retrieval_context.append(
                        f"[{tool_name}]\n{_safe_truncate(str(msg.content))}"
                    )

            title = title_generator(collect_query)
            report_input = (
                f"Title: {title}\n\n"
                f" Your day-by-day itinerary must contain exactly {days} day(s) — no more, no fewer."
                f"Trip Details:\n"
                f"- City: {city}\n"
                f"- Duration: {days} days\n"
                f"- Style: {style}\n"
                f"- Pace: {pace}\n"
                f"- Month: {month or 'Any'}\n"
                f"- Currency: {currency or 'USD'}\n\n"
                f"Research Data:\n"
                + "\n\n---\n\n".join(retrieval_context)
            )

            config = {"configurable": {"thread_id": thread_id}}

            report_response = report_agent.invoke(
                {"messages": [HumanMessage(content=report_input)]},
                config=config,
            )

            history = report_response.get("messages", [])
            final_report = history[-1].content if history else ""

            structuring_input = (
                f"Travel Report:\n\n"
                f"{final_report}\n\n"
                f"Supporting Research:\n\n"
                + "\n\n---\n\n".join(retrieval_context)
            )

            logger.info("Generating structured TravelPlan")
            structured_itinerary = structured_model.invoke(structuring_input)
            

            return {
                
                "itinerary": structured_itinerary,
                "title": title, 
                "tool_calls": tool_calls,
                "retrieval_context": retrieval_context,
                "thread_id": thread_id,
            }

        except Exception:
            logger.exception("Failed to generate itinerary")
            raise