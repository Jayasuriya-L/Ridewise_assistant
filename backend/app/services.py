from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from .auth import AccessControl
from .database import (
    get_customer,
    get_bookings_for_customer,
    get_booking_for_support,
    get_payments_for_customer,
    get_payments_for_booking,
    get_damage_reports_for_customer,
    get_damage_reports_for_booking,
    get_vehicle_details,
    search_vehicles
)
from .policy_retrieval import policy_retriever
from .query_router import query_router
from .llm import llm_client
from .schemas import ChatRequest, ChatResponse

# Deterministic calculation helpers
def calculate_refund_eligibility(booking: Dict[str, Any], cancel_time_utc: Optional[datetime] = None) -> Dict[str, Any]:
    """
    Computes deterministic refund eligibility under Policy v1 or v2 based strictly on booked_at time.
    """
    booked_at_str = booking.get("booked_at")
    sched_start_str = booking.get("scheduled_start")
    cancelled_at_str = booking.get("cancelled_at")

    policy_doc = policy_retriever.determine_applicable_refund_policy(booked_at_str)
    is_v2 = (policy_doc == "03_Cancellation_and_Refund_Policy_v2.pdf")

    # Determine reference cancellation time
    if cancelled_at_str:
        ref_cancel_dt = datetime.strptime(cancelled_at_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
    elif cancel_time_utc:
        ref_cancel_dt = cancel_time_utc
    else:
        # Hypothetical current cancellation
        ref_cancel_dt = datetime.now(timezone.utc)

    sched_start_dt = datetime.strptime(sched_start_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
    diff_hours = (sched_start_dt - ref_cancel_dt).total_seconds() / 3600.0

    refund_pct = 0.0
    if booking.get("booking_status") == "CNL_S":
        refund_pct = 100.0
        reason = "RideWise cancelled the booking (100% full refund policy)"
    elif diff_hours < 0:
        refund_pct = 0.0
        reason = "Cancellation request after scheduled pickup time (0% refund / no-show rules)"
    else:
        if is_v2:
            # Policy Version 2:
            # >= 48 hours: 100%
            # >= 12 and < 48: 75%
            # >= 2 and < 12: 25%
            # < 2 hours: 0%
            if diff_hours >= 48.0:
                refund_pct = 100.0
            elif diff_hours >= 12.0:
                refund_pct = 75.0
            elif diff_hours >= 2.0:
                refund_pct = 25.0
            else:
                refund_pct = 0.0
            reason = f"Policy v2 Annexure 1 evaluated {diff_hours:.1f} hours before pickup"
        else:
            # Policy Version 1:
            # >= 24 hours: 100%
            # >= 6 and < 24: 50%
            # < 6 hours: 0%
            if diff_hours >= 24.0:
                refund_pct = 100.0
            elif diff_hours >= 6.0:
                refund_pct = 50.0
            else:
                refund_pct = 0.0
            reason = f"Policy v1 evaluated {diff_hours:.1f} hours before pickup"

    return {
        "applicable_policy_version": "Version 2 (RW-POL-03)" if is_v2 else "Version 1 (RW-POL-02)",
        "policy_document": policy_doc,
        "eligible_refund_percent": refund_pct,
        "hours_before_pickup": round(diff_hours, 2),
        "evaluation_notes": reason
    }

class RideWiseService:
    @staticmethod
    def process_chat(req: ChatRequest) -> ChatResponse:
        auth_context = AccessControl.validate_user_role(req.role, req.customer_id)
        role = auth_context["role"]
        customer = auth_context["customer"]

        # Extract entities from query
        entities = query_router.extract_entities(req.message)
        effective_booking_id = entities["booking_id"] or (req.booking_id.strip() if req.booking_id else None)

        # Enforce customer ownership check if query mentions a booking
        if effective_booking_id and role == "CUSTOMER":
            customer_bookings = get_bookings_for_customer(customer["customer_id"], effective_booking_id)
            if not customer_bookings:
                # Check if this booking belongs to someone else
                support_check = get_booking_for_support(effective_booking_id)
                if support_check:
                    AccessControl.assert_customer_ownership(auth_context, support_check["customer_id"])

        # Classify query
        query_type = query_router.classify(req.message, has_booking_context=bool(effective_booking_id))

        db_context: Dict[str, Any] = {}
        sources: List[str] = []
        target_policy_file: Optional[str] = None

        # 1. Gather Database Context
        if role == "CUSTOMER":
            db_context["authenticated_customer"] = {
                "customer_id": customer["customer_id"],
                "full_name": customer["full_name"],
                "customer_tier": customer["customer_tier"],
                "kyc_status": customer["kyc_status"]
            }
            sources.append("ridewise.db (customers)")

            if effective_booking_id:
                bookings = get_bookings_for_customer(customer["customer_id"], effective_booking_id)
                if bookings:
                    b = bookings[0]
                    db_context["target_booking"] = b
                    sources.append("ridewise.db (bookings)")
                    payments = get_payments_for_booking(effective_booking_id)
                    db_context["booking_payments"] = payments
                    sources.append("ridewise.db (payments)")
                    damages = get_damage_reports_for_booking(effective_booking_id)
                    db_context["booking_damages"] = damages
                    if damages:
                        sources.append("ridewise.db (damage_reports)")

                    # Check which policy version applies
                    target_policy_file = policy_retriever.determine_applicable_refund_policy(b["booked_at"])
                    # Deterministic refund calculation
                    refund_calc = calculate_refund_eligibility(b)
                    db_context["deterministic_refund_analysis"] = refund_calc

                    # Check recorded refund transactions in payments
                    refund_payments = [p for p in payments if p.get("payment_type") == "REFUND"]
                    db_context["recorded_refund_transactions"] = refund_payments
            else:
                # Retrieve all customer bookings and payments summary
                all_b = get_bookings_for_customer(customer["customer_id"])
                db_context["customer_recent_bookings"] = all_b[:5]
                sources.append("ridewise.db (bookings)")

        elif role == "SUPPORT_AGENT":
            db_context["agent_session"] = {"role": "SUPPORT_AGENT"}
            if effective_booking_id:
                b = get_booking_for_support(effective_booking_id)
                if b:
                    db_context["target_booking"] = b
                    sources.append("ridewise.db (bookings, customers, vehicles)")
                    payments = get_payments_for_booking(effective_booking_id)
                    db_context["booking_payments"] = payments
                    sources.append("ridewise.db (payments)")
                    damages = get_damage_reports_for_booking(effective_booking_id)
                    db_context["booking_damages"] = damages
                    if damages:
                        sources.append("ridewise.db (damage_reports)")

                    target_policy_file = policy_retriever.determine_applicable_refund_policy(b["booked_at"])
                    refund_calc = calculate_refund_eligibility(b)
                    db_context["deterministic_refund_analysis"] = refund_calc
                    db_context["recorded_refund_transactions"] = [p for p in payments if p.get("payment_type") == "REFUND"]
            elif entities["customer_id"]:
                c = get_customer(entities["customer_id"])
                if c:
                    db_context["inspected_customer"] = c
                    db_context["customer_bookings"] = get_bookings_for_customer(c["customer_id"])
                    sources.append("ridewise.db (customers, bookings)")

        # 2. Gather Policy Context
        retrieved_policy_chunks = []
        if query_type in ["POLICY", "HYBRID", "GENERAL"] or not db_context.get("target_booking"):
            retrieved_policy_chunks = policy_retriever.retrieve(
                query=req.message,
                top_k=3,
                target_policy_version=target_policy_file
            )
            for chunk in retrieved_policy_chunks:
                if chunk["doc_name"] not in sources:
                    sources.append(chunk["doc_name"])

        # 3. Format Context for LLM
        data_context_str = None
        if db_context:
            import json
            data_context_str = json.dumps(db_context, indent=2, default=str)

        policy_context_str = None
        if retrieved_policy_chunks:
            policy_context_str = "\n\n".join([
                f"[{c['doc_name']} - Page {c['page']} - {c['section']}]:\n{c['content']}"
                for c in retrieved_policy_chunks
            ])

        # 4. Construct System Prompt
        system_prompt = (
            "You are RideWise Assist, an intelligent, precise, and honest customer support AI for RideWise Mobility.\n"
            "You assist customers and support agents using verified database records and policy documents.\n\n"
            "STRICT RULES:\n"
            "1. Ground all answers strictly in the provided operational database records and policy documents.\n"
            "2. Never hallucinate or invent policies, dates, booking IDs, or financial values.\n"
            "3. When discussing cancellation and refunds:\n"
            "   - Determine the policy version by booking creation time (Before 1 July 2026, 00:00 IST -> Version 1; On or after 1 July 2026, 00:00 IST -> Version 2).\n"
            "   - State the policy document name explicitly.\n"
            "   - Distinguish policy-based eligibility from recorded transactions: being eligible does NOT mean a refund has already been recorded unless an actual REFUND payment transaction exists in the database!\n"
            "4. For customer role, never disclose or discuss records of any other customer.\n"
            "5. Cite relevant document names (e.g. RW-POL-01, RW-POL-02, RW-POL-03, RW-POL-04, RW-POL-05) and database tables in your explanation.\n"
            "6. Keep answers concise, courteous, well-structured, and helpful."
        )

        # 5. Synthesize Answer
        history_list = [h.dict() for h in req.conversation_history] if req.conversation_history else []
        answer = llm_client.generate_response(
            system_prompt=system_prompt,
            user_message=req.message,
            conversation_history=history_list,
            data_context_str=data_context_str,
            policy_context_str=policy_context_str
        )

        return ChatResponse(
            answer=answer,
            role=role,
            query_type=query_type,
            sources=sources,
            data_context=db_context
        )
