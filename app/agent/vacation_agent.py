# app/agent/vacation_agent.py: PydanticAI agent with tools



# Agent I/O models
from __future__ import annotations

from datetime import date, timedelta
from typing import Optional, List

from pydantic import BaseModel, Field, ConfigDict
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.usage import UsageLimits

from ..config import get_settings
from ..models.domain import (
    UserPreferences,
    DateRange,
    FlightOption,
    HotelOption,
    VacationPlan,
    DayPlan,
)
from ..services.preferences import get_user_preferences
from ..services.calendar import find_free_date_ranges
from ..services.travel_search import mock_search_flights, mock_search_hotels


class AgentInput(BaseModel):
    """
    What the backend passes to the agent.
    """
    user_message: str
    user_id: str
    allow_booking: bool = False
    # If the user continues a conversation, you can optionally pass the current plan:
    current_plan: Optional[VacationPlan] = None


class AgentOutput(BaseModel):
    """
    What the agent returns:
    - a natural language reply
    - optionally an updated plan
    - whether the planner is asking for booking confirmation
    """
    assistant_message: str
    updated_plan: Optional[VacationPlan] = None
    ask_for_booking_confirmation: bool = False



# Instantiate the Agent
settings = get_settings()

# Configure the OpenAI model (GPT-5 nano, etc.)
openai_model = OpenAIChatModel(settings.openai_model_name, provider=OpenAIProvider(api_key=settings.openai_api_key))

AGENT_SYSTEM_PROMPT = """
You are a vacation planning assistant that proposes itineraries; you do NOT perform real-world bookings.

You have exactly these tools available:

- load_preferences() -> UserPreferences
- get_free_date_ranges(trip_duration_days: int) -> list[DateRange]
- search_flights_tool(origin: str, destination: str, start: date, end: date) -> list[FlightOption]
- search_hotels_tool(destination_city: str, start: date, end: date) -> list[HotelOption]
- build_vacation_plan(destination_city: str, start: date, end: date,
                    flight: FlightOption, hotel: HotelOption) -> VacationPlan

Hard rules:

1. Never call any tool whose name is not in the list above.
Do NOT invent tools for booking, payment, or anything else.

2. For a normal planning request (user gives destination + duration or dates),
you should use tools at most once each in this order:

a. Call load_preferences once at the beginning.
b. If the user did NOT specify exact dates, call get_free_date_ranges once
    to pick a suitable DateRange.
c. Call search_flights_tool once to pick a flight.
d. Call search_hotels_tool once to pick a hotel.
e. Call build_vacation_plan once using the chosen dates, flight, and hotel.

Do NOT loop or "try again" with different parameters unless the first
attempt completely fails (e.g. the tools return empty lists).

3. If information is missing (no destination, no duration, etc.):
- Do NOT call any tools.
- Instead, return an AgentOutput where:
    - assistant_message asks the user clear follow-up questions.
    - updated_plan is null.
    - ask_for_booking_confirmation is False.

4. When you are satisfied with the plan:
- Call the output tool exactly once with an AgentOutput object where:
    - assistant_message is a friendly explanation of the itinerary.
    - updated_plan is the VacationPlan returned by build_vacation_plan.
    - ask_for_booking_confirmation is True only if the user explicitly
        asked you to book, otherwise False.

5. You never process raw payment details and never treat anything as "booked".
"""

vacation_agent: Agent[AgentInput, AgentOutput] = Agent(
    model=openai_model,
    deps_type=AgentInput,
    output_type=AgentOutput,
    system_prompt=AGENT_SYSTEM_PROMPT,
)



# Tools for the agent

@vacation_agent.tool
def load_preferences(ctx: RunContext[AgentInput]) -> UserPreferences:
    """
    Load user preferences from the storage layer.
    """
    return get_user_preferences(ctx.deps.user_id)


@vacation_agent.tool
def get_free_date_ranges(
    ctx: RunContext[AgentInput],
    trip_duration_days: int,
) -> list[DateRange]:
    """
    Find free date ranges in the next 60 days that can fit the requested trip duration.
    """
    user_id = ctx.deps.user_id
    return find_free_date_ranges(
        user_id=user_id,
        trip_duration_days=trip_duration_days,
        window_days=60,
    )


@vacation_agent.tool
def search_flights_tool(
    ctx: RunContext[AgentInput],
    origin: str,
    destination: str,
    start: date,
    end: date,
) -> list[FlightOption]:
    """
    Search mock flights between origin and destination near the chosen dates.
    """
    prefs = get_user_preferences(ctx.deps.user_id)
    max_budget = prefs.max_budget_total or prefs.max_budget_per_day
    date_range = DateRange(start=start, end=end)
    return mock_search_flights(
        origin=origin,
        destination=destination,
        date_range=date_range,
        max_budget=max_budget,
        currency=prefs.default_currency,
    )


@vacation_agent.tool
def search_hotels_tool(
    ctx: RunContext[AgentInput],
    destination_city: str,
    start: date,
    end: date,
) -> list[HotelOption]:
    """
    Search mock hotels for the chosen date range.
    """
    prefs = get_user_preferences(ctx.deps.user_id)
    max_total = prefs.max_budget_total
    return mock_search_hotels(
        destination_city=destination_city,
        start_date=start,
        end_date=end,
        max_budget_total=max_total,
        currency=prefs.default_currency,
    )

class BuildVacationPlanArgs(BaseModel):
    destination_city: str
    start: date
    end: date
    flight: FlightOption
    hotel: HotelOption

    # Ignore any extra fields the model sends (daily_plans, currency, etc.)
    model_config = ConfigDict(extra="ignore")

@vacation_agent.tool
def build_vacation_plan(
    ctx: RunContext[AgentInput],
    args: BuildVacationPlanArgs,
) -> VacationPlan:
    """
    Construct a VacationPlan from chosen options.

    NOTE:
    - The LLM may send extra fields (daily_plans, currency, estimated_total_cost, etc.)
    in the tool call.
    Because BuildVacationPlanArgs has extra='ignore', those are silently dropped.
    """
    prefs = get_user_preferences(ctx.deps.user_id)

    destination_city = args.destination_city
    start = args.start
    end = args.end
    flight = args.flight
    hotel = args.hotel

    # Number of days; ensure at least 1
    num_days = (end - start).days
    if num_days <= 0:
        num_days = 1

    # Naive total cost: flight + hotel total
    total_cost = flight.price + hotel.total_price

    daily_plans: List[DayPlan] = []
    for i in range(num_days):
        day_date = start + timedelta(days=i)
        daily_plans.append(
            DayPlan(
                date=day_date,
                morning=f"Explore a local attraction in {destination_city}.",
                afternoon=(
                    f"Enjoy something related to your interests: "
                    f"{', '.join(prefs.interests) or 'free time'}."
                ),
                evening=f"Dinner at a recommended spot in {destination_city}.",
                notes=None,
            )
        )

    plan = VacationPlan(
        user_id=ctx.deps.user_id,
        destination_city=destination_city,
        start_date=start,
        end_date=end,
        flight=flight,
        hotel=hotel,
        daily_plans=daily_plans,
        estimated_total_cost=total_cost,
        currency=prefs.default_currency,
        status="planned",
    )
    return plan



# Agent run helper
async def run_vacation_agent(
    user_message: str,
    user_id: str,
    allow_booking: bool = False,
    current_plan: Optional[VacationPlan] = None,
) -> AgentOutput:
    agent_input = AgentInput(
        user_message=user_message,
        user_id=user_id,
        allow_booking=allow_booking,
        current_plan=current_plan,
    )

    usage_limits = UsageLimits(
        request_limit=20,     # still generous for a simple plan
        tool_calls_limit=10,   # e.g. 5 tools + some slack
    )

    result = await vacation_agent.run(
        agent_input.user_message,
        deps=agent_input,
        usage_limits=usage_limits,
    )
    return result.output
