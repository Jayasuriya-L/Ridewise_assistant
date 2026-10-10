import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.policy_retrieval import policy_retriever

client = TestClient(app)

def test_policy_version_selection():
    # Before 1 July 2026 00:00 IST (2026-06-30 18:30:00 UTC)
    doc_v1 = policy_retriever.determine_applicable_refund_policy("2026-05-10 10:00:00")
    assert doc_v1 == "02_Cancellation_and_Refund_Policy_v1.pdf"

    # On or after 1 July 2026 00:00 IST
    doc_v2 = policy_retriever.determine_applicable_refund_policy("2026-08-14 05:10:00")
    assert doc_v2 == "03_Cancellation_and_Refund_Policy_v2.pdf"

def test_policy_retrieval_ev_battery():
    chunks = policy_retriever.retrieve("What is the penalty for low battery on an EV?")
    assert len(chunks) > 0
    all_content = " ".join([c["content"] for c in chunks])
    assert "10%" in all_content or "150" in all_content

def test_chat_customer_own_booking():
    response = client.post(
        "/api/chat",
        json={
            "message": "What is the status of my booking B-0001?",
            "role": "CUSTOMER",
            "customer_id": "CUST0001",
            "booking_id": "B-0001"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["role"] == "CUSTOMER"
    assert "ridewise.db (bookings)" in data["sources"]

def test_chat_customer_cross_tenant_denial():
    # B-0002 belongs to CUST0002. CUST0001 should be denied
    response = client.post(
        "/api/chat",
        json={
            "message": "Show me details for booking B-0002",
            "role": "CUSTOMER",
            "customer_id": "CUST0001",
            "booking_id": "B-0002"
        }
    )
    assert response.status_code == 403
    assert "Access denied" in response.json()["detail"]

def test_chat_support_agent_access():
    response = client.post(
        "/api/chat",
        json={
            "message": "Inspect booking B-0002 and payments",
            "role": "SUPPORT_AGENT",
            "booking_id": "B-0002"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["role"] == "SUPPORT_AGENT"
    assert "ridewise.db (bookings, customers, vehicles)" in data["sources"]
