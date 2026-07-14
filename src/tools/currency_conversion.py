

import os
import requests
from pydantic import BaseModel, Field, field_validator
from langchain.tools import tool
from dotenv import load_dotenv
load_dotenv()
API_KEY = os.getenv("EXCHANGE_RATE_API_KEY")
from src.config.config import *

class ConvertCurrencyInput(BaseModel):
    amount: str = Field(description="The amount to convert, as a plain number e.g. '1000'")
    from_currency: str = Field(description="Source currency code, e.g. 'USD'")
    to_currency: str = Field(description="Target currency code, e.g. 'NPR'")

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v):
        try:
            float(v)
        except (ValueError, TypeError):
            raise ValueError(f"amount must be numeric, got: {v!r}")
        return v


@tool(args_schema=ConvertCurrencyInput)
def convert_currency(amount: str, from_currency: str, to_currency: str) -> str:
    """
    Converts an amount from one currency to another (e.g., USD to EUR).
    Use this for all currency conversion needs.
    """
    if not API_KEY:
        return "Error: EXCHANGE_RATE_API_KEY is not configured."

    try:
        amount_val = float(amount)
    except (ValueError, TypeError):
        return f"Error: could not parse amount '{amount}' as a number."

    url = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/{from_currency.upper()}"

    try:
        response = requests.get(url, timeout=10)
        data = response.json()

        if data.get("result") != "success":
            return f"Error: Could not fetch rates. {data.get('error-type', 'Unknown error')}"

        rates = data.get("conversion_rates", {})
        target = to_currency.upper()

        if target not in rates:
            return f"Error: Target currency '{target}' not found."

        converted_amount = round(amount_val * rates[target], 2)
        return f"{amount_val} {from_currency.upper()} is {converted_amount} {target}."

    except Exception as e:
        return f"Conversion failed: {str(e)}"