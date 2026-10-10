import pytest
from app.database import (
    get_customer,
    get_bookings_for_customer,
    get_payments_for_customer,
    get_damage_reports_for_booking,
    get_vehicle_details
)

def test_customer_lookup():
    cust = get_customer("CUST0001")
    assert cust is not None
    assert cust["customer_id"] == "CUST0001"
    assert cust["full_name"] == "Aarav Sharma"
    assert cust["customer_tier"] == "GOLD"

def test_customer_bookings():
    bookings = get_bookings_for_customer("CUST0001")
    assert isinstance(bookings, list)
    assert len(bookings) > 0
    assert bookings[0]["customer_id"] == "CUST0001"

def test_customer_payments():
    payments = get_payments_for_customer("CUST0001")
    assert isinstance(payments, list)
    assert len(payments) > 0

def test_damage_reports():
    damages = get_damage_reports_for_booking("B-0002")
    assert isinstance(damages, list)
    if damages:
        assert damages[0]["booking_id"] == "B-0002"
        assert damages[0]["assessed_cost"] > 0

def test_vehicle_lookup():
    veh = get_vehicle_details("VEH001")
    assert veh is not None
    assert veh["vehicle_id"] == "VEH001"
    assert "Classic 350" in veh["model"]
