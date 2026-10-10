from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from .database import get_customer

class AccessControl:
    @staticmethod
    def validate_user_role(role: str, customer_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Validate incoming role and credentials.
        Returns customer profile if role is CUSTOMER.
        """
        normalized_role = role.strip().upper()
        if normalized_role not in ["CUSTOMER", "SUPPORT_AGENT"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid role '{role}'. Must be 'CUSTOMER' or 'SUPPORT_AGENT'."
            )
        
        if normalized_role == "CUSTOMER":
            if not customer_id or not customer_id.strip():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="customer_id is required when role is CUSTOMER."
                )
            
            clean_customer_id = customer_id.strip().upper()
            customer = get_customer(clean_customer_id)
            if not customer:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Customer ID '{clean_customer_id}' does not exist in RideWise records."
                )
            return {"role": "CUSTOMER", "customer": customer}
            
        return {"role": "SUPPORT_AGENT", "customer": None}

    @staticmethod
    def assert_customer_ownership(auth_context: Dict[str, Any], target_customer_id: str) -> None:
        """
        Enforce that a CUSTOMER cannot access or reference another customer's data.
        """
        if auth_context["role"] == "CUSTOMER":
            authenticated_id = auth_context["customer"]["customer_id"]
            if target_customer_id.strip().upper() != authenticated_id.strip().upper():
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied: You are not authorized to view records belonging to another customer."
                )
