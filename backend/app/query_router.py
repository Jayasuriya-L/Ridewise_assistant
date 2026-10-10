import re
from typing import Dict, Any, List, Optional

class QueryRouter:
    # Common entity patterns
    BOOKING_REGEX = re.compile(r'\bB-\d{4}\b', re.IGNORECASE)
    CUSTOMER_REGEX = re.compile(r'\bCUST\d{4}\b', re.IGNORECASE)
    VEHICLE_REGEX = re.compile(r'\bVEH\d{3}\b', re.IGNORECASE)
    DAMAGE_REGEX = re.compile(r'\bDMG\d{4}\b', re.IGNORECASE)
    PAYMENT_REGEX = re.compile(r'\bPAY\d{5}\b', re.IGNORECASE)

    # Keyword heuristics
    DB_KEYWORDS = [
        "my booking", "my bookings", "my account", "my payment", "my vehicle", "my damage",
        "booking id", "customer id", "reservation", "status", "scheduled", "transaction",
        "did i pay", "have i paid", "how much did i pay", "my receipt", "my invoice"
    ]

    POLICY_KEYWORDS = [
        "policy", "rule", "terms", "condition", "refund percent", "how much refund",
        "grace period", "penalty rate", "cancellation policy", "low battery", "ev guide",
        "charging", "kyc required", "hourly rate rule", "deposit rule"
    ]

    HYBRID_INDICATORS = [
        "eligible for refund", "can i cancel my booking", "how much refund for booking",
        "why was i charged", "penalty for booking", "my tier benefit", "cancel b-"
    ]

    @classmethod
    def extract_entities(cls, text: str) -> Dict[str, Optional[str]]:
        """Extract explicit identifiers from text."""
        booking_match = cls.BOOKING_REGEX.search(text)
        customer_match = cls.CUSTOMER_REGEX.search(text)
        vehicle_match = cls.VEHICLE_REGEX.search(text)
        damage_match = cls.DAMAGE_REGEX.search(text)
        payment_match = cls.PAYMENT_REGEX.search(text)

        return {
            "booking_id": booking_match.group(0).upper() if booking_match else None,
            "customer_id": customer_match.group(0).upper() if customer_match else None,
            "vehicle_id": vehicle_match.group(0).upper() if vehicle_match else None,
            "damage_id": damage_match.group(0).upper() if damage_match else None,
            "payment_id": payment_match.group(0).upper() if payment_match else None,
        }

    @classmethod
    def classify(cls, query: str, has_booking_context: bool = False) -> str:
        """
        Classifies query into: DATABASE, POLICY, HYBRID, or GENERAL.
        """
        text = query.lower()

        # Check hybrid first
        has_entities = bool(cls.extract_entities(query)["booking_id"]) or has_booking_context
        is_hybrid_phrase = any(phrase in text for phrase in cls.HYBRID_INDICATORS)
        has_policy_words = any(w in text for w in cls.POLICY_KEYWORDS)
        has_db_words = any(w in text for w in cls.DB_KEYWORDS)

        if (has_entities or has_db_words) and has_policy_words:
            return "HYBRID"

        if is_hybrid_phrase:
            return "HYBRID"

        if has_db_words or has_entities:
            return "DATABASE"

        if has_policy_words:
            return "POLICY"

        # Check if greeting or generic
        greetings = ["hi", "hello", "hey", "good morning", "good evening", "who are you", "help"]
        if any(re.match(rf"^{g}\b", text) for g in greetings):
            return "GENERAL"

        # Default fallback to POLICY retrieval to catch general questions safely
        return "POLICY"

query_router = QueryRouter()
