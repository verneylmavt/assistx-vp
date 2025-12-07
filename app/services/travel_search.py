# app/services/travel_search.py: Travel search (mock flights/hotels)
from __future__ import annotations

from datetime import datetime, timedelta, date
from typing import List

from ..models.domain import FlightOption, HotelOption, DateRange


def mock_search_flights(
    origin: str,
    destination: str,
    date_range: DateRange,
    max_budget: float | None,
    currency: str,
) -> List[FlightOption]:
    """
    Return a small list of mocked flight options.
    In a real system this would call a GDS / airline API.
    """
    base_price = 300.0
    flights: List[FlightOption] = []
    for i in range(3):
        dep_date = date_range.start + timedelta(days=i)
        dep_time = datetime.combine(dep_date, datetime.min.time()).replace(hour=9 + i)
        arr_time = dep_time + timedelta(hours=7)
        price = base_price + i * 50
        if max_budget is not None and price > max_budget:
            continue

        flights.append(
            FlightOption(
                id=f"FL-{origin}-{destination}-{i}",
                origin=origin,
                destination=destination,
                departure=dep_time,
                arrival=arr_time,
                airline="Demo Air",
                cabin_class="economy",
                price=price,
                currency=currency,
            )
        )
    return flights


def mock_search_hotels(
    destination_city: str,
    start_date: date,
    end_date: date,
    max_budget_total: float | None,
    currency: str,
) -> List[HotelOption]:
    """
    Return a small list of mocked hotel options.
    """
    nights = (end_date - start_date).days
    if nights <= 0:
        nights = 1

    base_price_per_night = 80.0
    hotels: List[HotelOption] = []
    for i in range(3):
        price_per_night = base_price_per_night + i * 30
        total_price = price_per_night * nights
        if max_budget_total is not None and total_price > max_budget_total:
            continue
        hotels.append(
            HotelOption(
                id=f"HT-{destination_city}-{i}",
                destination_city=destination_city,
                name=f"Demo Hotel {i}",
                check_in=start_date,
                check_out=end_date,
                price_per_night=price_per_night,
                total_price=total_price,
                currency=currency,
                rating=3.5 + i * 0.5,
            )
        )
    return hotels