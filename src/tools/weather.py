import os
from collections import defaultdict
from datetime import datetime
import requests
from langchain.tools import tool
from dotenv import load_dotenv

load_dotenv()
OPENWEATHER_API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")
BASE_URL = "https://api.openweathermap.org/data/2.5"



@tool
def get_weather_forecast(city: str, days: int = 5) -> str:
    """Get a day-wise weather forecast summary for a specific city (e.g., 'Paris, FR').

    Args:
        city: Name of the city, e.g. "London" or "Paris, FR".
        days: Number of days to forecast (1-5). The free forecast API only
            provides up to 5 days of data, so higher values are capped.
    """
    if not OPENWEATHER_API_KEY:
        return "Error: OPENWEATHERMAP_API_KEY is not set."

    days = max(1, min(days, 5))

    url = f"{BASE_URL}/forecast"
    params = {"q": city, "appid": OPENWEATHER_API_KEY, "units": "metric"}

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if "list" not in data:
            return f"Could not fetch forecast for {city}."

        # Group the 3-hour interval entries by calendar date
        by_day = defaultdict(list)
        for item in data["list"]:
            date = item["dt_txt"].split(" ")[0]
            by_day[date].append(item)

        # Skip today (partial data) if there's more than one day available,
        # so "3-day forecast" means 3 full upcoming days, not today + 2.
        dates = list(by_day.keys())
        today_str = datetime.utcnow().strftime("%Y-%m-%d")
        if len(dates) > days and dates[0] == today_str:
            dates = dates[1:]

        selected_dates = dates[:days]

        lines = []
        for date in selected_dates:
            items = by_day[date]
            temps = [i["main"]["temp"] for i in items]
            desc = items[len(items) // 2]["weather"][0]["description"]  # midday-ish reading
            lines.append(f"{date}: {min(temps):.1f}–{max(temps):.1f}°C, {desc}")

        return f"{len(selected_dates)}-day weather forecast for {city}:\n" + "\n".join(lines)

    except requests.exceptions.HTTPError as e:
        if response.status_code == 404:
            return f"City '{city}' not found. Please check the spelling or try 'City, CountryCode' format."
        return f"Weather API error for {city}: {str(e)}"
    except requests.exceptions.Timeout:
        return f"Weather forecast request for {city} timed out. Please try again."
    except Exception as e:
        return f"Failed to fetch forecast for {city}. Error: {str(e)}"