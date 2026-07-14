from pydantic import BaseModel, Field
from typing import List, Optional


class Activity(BaseModel):
    """Represent a single activity in an itinerary"""
    time: str = Field(description="Time of the day for an activity include Morning, Afternoon, Evening if possible")
    description: str = Field(description="Detailed description for an activity")
    location: str = Field(description="Name of the place or attraction")


class HotelOption(BaseModel):
    name: str = Field(description="Hotel name")
    price_per_night: Optional[float] = Field(default=None,description="Price per night in Available currency (USD, EUR, etc.)")
    rating: Optional[float] = Field(default=None,description="Hotel star rating or user rating"
)
class DiningRecommendation(BaseModel):
    restaurant_name: str = Field(description="Name of the restaurant, cafe, or street food stall")
    meal: str = Field(description="Which meal this is for (e.g., Breakfast, Lunch, Dinner, Snack)")
    famous_dishes: List[str] = Field(description="At least 2 specific famous dishes or specialties to try here")
class DayPlan(BaseModel):
    """Represent a full day's plan"""
    day_number: int = Field(description="The day number in the trip")
    theme: str = Field(description="The main theme of the day ")
    activities: List[Activity] = Field(description="List of activities for the day suggest at least 3 activities nearby each other ")
    weather: Optional[str] = Field(default=None, description="Short weather note for this specific day with temperature, precipitation, and any relevant weather warnings")
    dining_recommendations: List[DiningRecommendation] = Field(default_factory=list, description="Recommended places to eat for the day")
    transportation: List[str] = Field(default_factory=list, description="Transportation options for the day")


class TravelPlan(BaseModel):
    """The final structured travel itinerary"""
    city: str = Field(description="Destination City")
    
    weather_summary: Optional[str] = Field(default=None, description="Day-wise weather forecast overview for the trip duration")
    total_days: int = Field(description="Number of days planned")
    itinerary: List[DayPlan] = Field(description="The day-by-day plan")
    hotel_options: List[HotelOption] = Field(default_factory=list)
    transportation_options: List[str] = Field(default_factory=list, description="Ways to get around the destination suggest at least 3 options.")
    currency_note: Optional[str] = Field(default=None, description="A currency conversion reference relevant to the traveler's budget if user specified a currency")
    final_recommendations: List[str] = Field(default_factory=list, description="generic advice for a trip")
    travel_warnings: List[str] = Field(default_factory=list, description="Safety warnings, travel advisories, or scam alerts for the destination")
    estimated_budget_category: str = Field(description="Budget category (Budget, Mid-range, Luxury)")
    
