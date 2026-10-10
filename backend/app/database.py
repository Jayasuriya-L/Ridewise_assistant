import sqlite3
from typing import List, Dict, Any, Optional
from .config import get_verified_db_path

def get_db_connection() -> sqlite3.Connection:
    """Returns a read-only SQLite connection with row factory enabled."""
    db_path = get_verified_db_path()
    # Read-only connection to guarantee no modification of original database
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn

def get_customer(customer_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve customer profile by customer_id."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT customer_id, full_name, phone, email, city, date_of_birth, driving_license_no, kyc_status, customer_tier, created_at "
            "FROM customers WHERE customer_id = ?",
            (customer_id,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None

def get_bookings_for_customer(customer_id: str, booking_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieve bookings belonging strictly to the customer."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        query = (
            "SELECT b.booking_id, b.customer_id, b.vehicle_id, b.booked_at, "
            "b.scheduled_start, b.scheduled_end, b.actual_return_at, b.cancelled_at, "
            "b.booking_status, b.return_battery_pct, "
            "v.model, v.registration_no, v.vehicle_type, v.hub_name, v.hourly_rate, v.daily_rate "
            "FROM bookings b "
            "LEFT JOIN vehicles v ON b.vehicle_id = v.vehicle_id "
            "WHERE b.customer_id = ?"
        )
        params: List[Any] = [customer_id]
        if booking_id:
            query += " AND b.booking_id = ?"
            params.append(booking_id)
        query += " ORDER BY b.booked_at DESC"
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

def get_booking_for_support(booking_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve any booking for support agent."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT b.booking_id, b.customer_id, b.vehicle_id, b.booked_at, "
            "b.scheduled_start, b.scheduled_end, b.actual_return_at, b.cancelled_at, "
            "b.booking_status, b.return_battery_pct, "
            "c.full_name, c.phone, c.email, c.customer_tier, "
            "v.model, v.registration_no, v.vehicle_type, v.hub_name, v.hourly_rate, v.daily_rate "
            "FROM bookings b "
            "LEFT JOIN customers c ON b.customer_id = c.customer_id "
            "LEFT JOIN vehicles v ON b.vehicle_id = v.vehicle_id "
            "WHERE b.booking_id = ?",
            (booking_id,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None

def get_payments_for_customer(customer_id: str, booking_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieve payments belonging strictly to customer's bookings."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        query = (
            "SELECT p.payment_id, p.booking_id, p.payment_type, p.amount, p.gst_amount, "
            "p.payment_method, p.payment_status, p.transaction_ref, p.paid_at, p.remarks "
            "FROM payments p "
            "JOIN bookings b ON p.booking_id = b.booking_id "
            "WHERE b.customer_id = ?"
        )
        params: List[Any] = [customer_id]
        if booking_id:
            query += " AND b.booking_id = ?"
            params.append(booking_id)
        query += " ORDER BY p.paid_at DESC"
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

def get_payments_for_booking(booking_id: str) -> List[Dict[str, Any]]:
    """Retrieve all payments for a booking (used by support or verified customer)."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT payment_id, booking_id, payment_type, amount, gst_amount, "
            "payment_method, payment_status, transaction_ref, paid_at, remarks "
            "FROM payments WHERE booking_id = ? ORDER BY paid_at ASC",
            (booking_id,)
        )
        return [dict(row) for row in cursor.fetchall()]

def get_damage_reports_for_customer(customer_id: str, booking_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieve damage reports belonging strictly to customer's bookings."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        query = (
            "SELECT d.report_id, d.booking_id, d.vehicle_id, d.reported_by, "
            "d.damage_category, d.severity, d.description, d.assessed_cost, "
            "d.claim_status, d.reported_at "
            "FROM damage_reports d "
            "JOIN bookings b ON d.booking_id = b.booking_id "
            "WHERE b.customer_id = ?"
        )
        params: List[Any] = [customer_id]
        if booking_id:
            query += " AND d.booking_id = ?"
            params.append(booking_id)
        query += " ORDER BY d.reported_at DESC"
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

def get_damage_reports_for_booking(booking_id: str) -> List[Dict[str, Any]]:
    """Retrieve damage reports for a booking."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT report_id, booking_id, vehicle_id, reported_by, "
            "damage_category, severity, description, assessed_cost, "
            "claim_status, reported_at "
            "FROM damage_reports WHERE booking_id = ? ORDER BY reported_at ASC",
            (booking_id,)
        )
        return [dict(row) for row in cursor.fetchall()]

def get_vehicle_details(vehicle_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve vehicle details by vehicle_id."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT vehicle_id, registration_no, vehicle_type, model, hub_name, "
            "hourly_rate, daily_rate, battery_capacity_kwh, status, commissioned_on "
            "FROM vehicles WHERE vehicle_id = ?",
            (vehicle_id,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None

def search_vehicles(hub_name: Optional[str] = None, vehicle_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """Search vehicles by hub or vehicle type."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM vehicles WHERE status = 'ACTIVE'"
        params = []
        if hub_name:
            query += " AND LOWER(hub_name) LIKE LOWER(?)"
            params.append(f"%{hub_name}%")
        if vehicle_type:
            query += " AND LOWER(vehicle_type) = LOWER(?)"
            params.append(vehicle_type)
        query += " ORDER BY model ASC"
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
