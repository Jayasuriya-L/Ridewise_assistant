import pytest
from fastapi import HTTPException
from app.auth import AccessControl

def test_customer_role_requires_customer_id():
    with pytest.raises(HTTPException) as exc_info:
        AccessControl.validate_user_role("CUSTOMER", customer_id="")
    assert exc_info.value.status_code == 400

def test_invalid_customer_id():
    with pytest.raises(HTTPException) as exc_info:
        AccessControl.validate_user_role("CUSTOMER", customer_id="NON_EXISTENT_ID")
    assert exc_info.value.status_code == 404

def test_valid_customer_role():
    ctx = AccessControl.validate_user_role("CUSTOMER", customer_id="CUST0001")
    assert ctx["role"] == "CUSTOMER"
    assert ctx["customer"]["customer_id"] == "CUST0001"

def test_support_agent_role():
    ctx = AccessControl.validate_user_role("SUPPORT_AGENT")
    assert ctx["role"] == "SUPPORT_AGENT"
    assert ctx["customer"] is None

def test_customer_ownership_enforcement():
    ctx = AccessControl.validate_user_role("CUSTOMER", customer_id="CUST0001")
    
    # Authorized access to own ID
    AccessControl.assert_customer_ownership(ctx, "CUST0001")

    # Forbidden access to another customer's ID
    with pytest.raises(HTTPException) as exc_info:
        AccessControl.assert_customer_ownership(ctx, "CUST0002")
    assert exc_info.value.status_code == 403
