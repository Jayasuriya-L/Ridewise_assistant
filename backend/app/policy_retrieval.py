import os
import re
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone, timedelta
from pypdf import PdfReader
from .config import settings

# 1 July 2026 00:00 IST = 30 June 2026 18:30:00 UTC
POLICY_V2_CUTOFF_UTC = datetime(2026, 6, 30, 18, 30, 0, tzinfo=timezone.utc)

# Transcribed signed / scanned annexures verified via document OCR & inspection
SCANNED_ANNEXURES = {
    "03_Cancellation_and_Refund_Policy_v2.pdf": (
        "Annexure 1: Refund schedule (Version 2) - Approved by RideWise Policy Committee on 20 June 2026.\n"
        "Applies strictly to bookings made ON OR AFTER 1 July 2026, 00:00 IST.\n"
        "Cancellation timeline before scheduled pickup:\n"
        "• 48 hours or more: 100% refund of rental charge.\n"
        "• 12 hours or more, but less than 48 hours: 75% refund of rental charge.\n"
        "• 2 hours or more, but less than 12 hours: 25% refund of rental charge.\n"
        "• Less than 2 hours: No refund (0%).\n"
        "Cancelled by RideWise: 100% refund in all cases.\n"
        "No-show: No refund (0%). Security deposits are returned in full."
    ),
    "04_Late_Return_and_Damage_Penalty_Schedule.pdf": (
        "Annexure A: Tier Benefits - Approved by RideWise Policy Committee on 15 December 2024.\n"
        "Late return grace period by customer tier:\n"
        "• STANDARD: None (No grace period; charged 1.5x hourly rate per late hour/part-hour from minute 1).\n"
        "• SILVER: None (No grace period; charged 1.5x hourly rate per late hour/part-hour from minute 1).\n"
        "• GOLD: 30 minutes grace period (up to and including 30 minutes late = no late fee).\n"
        "Important Rule: If a GOLD member returns more than 30 minutes late, the full lateness is charged "
        "from the first minute, exactly as for other tiers (the grace period does not reduce billable hours)."
    )
}

class PolicyDocumentChunk:
    def __init__(self, doc_name: str, page: int, section: str, content: str):
        self.doc_name = doc_name
        self.page = page
        self.section = section
        self.content = content.strip()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "doc_name": self.doc_name,
            "page": self.page,
            "section": self.section,
            "content": self.content
        }

class PolicyRetriever:
    def __init__(self, policy_dir: Optional[str] = None):
        self.policy_dir = policy_dir or settings.POLICY_DIR
        self.chunks: List[PolicyDocumentChunk] = []
        self._load_and_index_policies()

    def _load_and_index_policies(self):
        """Extract text from the 5 supplied PDFs and build searchable chunks."""
        expected_files = [
            "01_Rental_Agreement_and_Terms.pdf",
            "02_Cancellation_and_Refund_Policy_v1.pdf",
            "03_Cancellation_and_Refund_Policy_v2.pdf",
            "04_Late_Return_and_Damage_Penalty_Schedule.pdf",
            "05_EV_User_Guide_and_FAQ.pdf"
        ]

        for fname in expected_files:
            file_path = os.path.join(self.policy_dir, fname)
            if not os.path.isfile(file_path):
                continue

            try:
                reader = PdfReader(file_path)
                for page_idx, page in enumerate(reader.pages):
                    raw_text = page.extract_text() or ""
                    
                    # If this page has a scanned annexure, supplement it
                    if fname in SCANNED_ANNEXURES and (
                        ("Annexure 1" in raw_text or "scanned" in raw_text.lower()) if fname == "03_Cancellation_and_Refund_Policy_v2.pdf"
                        else ("Annexure A" in raw_text or page_idx == 2)
                    ):
                        raw_text += "\n\n" + SCANNED_ANNEXURES[fname]

                    # Break page into section chunks
                    sections = re.split(r'\n(?=[0-9]+\.\s+[A-Z]|Annexure|Q\.)', raw_text)
                    for sec in sections:
                        sec_clean = sec.strip()
                        if len(sec_clean) < 30:
                            continue
                        
                        first_line = sec_clean.split("\n")[0][:60]
                        self.chunks.append(
                            PolicyDocumentChunk(
                                doc_name=fname,
                                page=page_idx + 1,
                                section=first_line,
                                content=sec_clean
                            )
                        )
            except Exception as e:
                print(f"[PolicyRetriever] Error indexing {fname}: {e}")

    @staticmethod
    def determine_applicable_refund_policy(booked_at_utc_str: str) -> str:
        """
        Determines whether Version 1 or Version 2 applies based on booking creation timestamp.
        Cutoff is 1 July 2026, 00:00 IST (2026-06-30 18:30:00 UTC).
        """
        try:
            # Parse 'YYYY-MM-DD HH:MM:SS'
            dt = datetime.strptime(booked_at_utc_str.strip(), "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
            if dt >= POLICY_V2_CUTOFF_UTC:
                return "03_Cancellation_and_Refund_Policy_v2.pdf"
            else:
                return "02_Cancellation_and_Refund_Policy_v1.pdf"
        except Exception:
            return "03_Cancellation_and_Refund_Policy_v2.pdf"

    def retrieve(self, query: str, top_k: int = 3, target_policy_version: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Lightweight BM25/TF-IDF style term frequency matching.
        Optionally filters out obsolete cancellation policy versions when context is known.
        """
        if not self.chunks:
            return []

        # Tokenize query
        stop_words = {"the", "a", "an", "is", "in", "it", "of", "and", "or", "for", "to", "what", "how", "can", "i", "my", "on"}
        query_tokens = [w.lower() for w in re.findall(r'\b[a-zA-Z0-9_\-]+\b', query) if w.lower() not in stop_words]

        scored_chunks = []
        for chunk in self.chunks:
            # If target_policy_version is specified (e.g. v1 vs v2), suppress the other version
            if target_policy_version == "02_Cancellation_and_Refund_Policy_v1.pdf" and chunk.doc_name == "03_Cancellation_and_Refund_Policy_v2.pdf":
                continue
            if target_policy_version == "03_Cancellation_and_Refund_Policy_v2.pdf" and chunk.doc_name == "02_Cancellation_and_Refund_Policy_v1.pdf":
                continue

            content_lower = chunk.content.lower()
            section_lower = chunk.section.lower()
            score = 0.0

            for token in query_tokens:
                # Exact matches in section headers carry higher weight
                if token in section_lower:
                    score += 4.0
                # Matches in body
                matches = content_lower.count(token)
                if matches > 0:
                    score += 1.0 + min(matches * 0.5, 3.0)

            # Boost relevant domain terms
            if "refund" in query_tokens and "cancellation" in chunk.doc_name.lower():
                score += 3.0
            if "late" in query_tokens and "late" in chunk.doc_name.lower():
                score += 3.0
            if "battery" in query_tokens and ("ev" in chunk.doc_name.lower() or "penalty" in chunk.doc_name.lower()):
                score += 3.0

            if score > 0:
                scored_chunks.append((score, chunk))

        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        results = [c.to_dict() for _, c in scored_chunks[:top_k]]
        return results

# Singleton instance
policy_retriever = PolicyRetriever()
