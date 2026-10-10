# Architecture & Engineering Decisions (DECISIONS.md)

This document provides a transparent engineering breakdown of the key technical decisions, rejected alternatives, known failure cases, and upcoming roadmap for **RideWise Assist**.

---

## 1. Three Important Design Decisions

### Decision 1: Deterministic Calculations Outside the LLM
- **Decision**: All financial amounts, cancellation refund percentages, late return hour rounding (at 1.5x hourly rate), and tier grace periods are calculated deterministically in Python/SQL before prompting the LLM.
- **Why**: LLMs are notoriously prone to floating-point errors, hallucinated dates, and inconsistent boundary evaluation (e.g. evaluating 11.9 hours as "12 hours"). By calculating eligibility deterministically and passing the structured result to the LLM, we guarantee 100% mathematical fidelity and regulatory compliance.

### Decision 2: Temporal Policy Version Routing Based on `booked_at`
- **Decision**: A strict cutoff rule is applied to determine whether Cancellation & Refund Policy Version 1 (`02_Cancellation_and_Refund_Policy_v1.pdf`) or Version 2 (`03_Cancellation_and_Refund_Policy_v2.pdf`) applies. The cutoff is evaluated against **1 July 2026, 00:00 IST** (UTC equivalent: `2026-06-30 18:30:00 UTC`).
- **Why**: If both policy versions were simultaneously injected into the LLM context, the model would conflate the differing refund slabs (e.g., v1: 24h/6h slabs vs v2: 48h/12h/2h slabs). Grounding the retrieval query strictly to the policy that was in force when the customer booked avoids confusion.

### Decision 3: Backend-Enforced Tenant Ownership & Zero Raw SQL
- **Decision**: The system rejects customer requests that reference other customers' records at the authorization layer (`HTTP 403 Forbidden`). Additionally, the LLM is never given arbitrary SQL execution privileges; queries use parameterized SQL functions.
- **Why**: Prompt-level authorization ("Please do not reveal other customer's info") is vulnerable to prompt injection and jailbreaks. Moving authorization to the Python middleware creates an immutable security boundary.

---

## 2. Alternatives Considered & Rejected

1. **Text-to-SQL (Allowing the LLM to write arbitrary SQL)**:
   - *Rejected Because*: LLM-generated SQL creates severe SQL injection risks, unpredictable performance on large tables, and potential privilege escalation. Prepared parameterized queries provide deterministic safety.
2. **Dense Vector Embeddings & Vector Database (ChromaDB / Pinecone)**:
   - *Rejected Because*: With five well-structured policy documents (less than 20 pages total), heavy external vector databases introduce unnecessary memory overhead, model downloading latency, and embedding drift. A lightweight BM25/keyword retrieval system with section chunking is fast, transparent, and reproducible.
3. **Pure LLM OCR for Scanned Documents**:
   - *Rejected Because*: Running multimodal OCR over the network for every user query introduces unacceptable latency and costs. Inspecting and transcribing the signed scanned annexures (Policy v2 Annexure 1 & Penalty Schedule Annexure A) into the retrieval knowledge base provides instant, deterministic lookup.

---

## 3. Current Limitations & Failure Cases

1. **Complex Multi-Constraint Hypotheticals**:
   - If a user asks: "What if I was Gold tier, but my booking was made on June 30th at 11:59 PM, and I returned 31 minutes late?", the system handles it, but very convoluted chain-of-thought hypotheticals without explicit booking IDs rely more heavily on LLM synthesis.
2. **Rate Limits & API Outages**:
   - If the Azure OpenAI endpoint is throttled or times out, the system degrades to returning structured database records and policy excerpts rather than a synthesized conversational paragraph.
3. **Pre-Indexed Scanned Tables**:
   - If a new scanned PDF policy is uploaded at runtime without updating the document loader, purely scanned pages without selectable text streams would need an active OCR engine (e.g. pytesseract) installed on the host OS.

---

## 4. Improvements Planned for One Additional Week

1. **Async Vector Store with Hybrid Search**:
   - Implement hybrid sparse/dense retrieval combining BM25 and local sentence-transformers embeddings for handling nuanced semantic paraphrasing.
2. **Dynamic OCR Pipeline**:
   - Embed lightweight ONNX-based OCR (such as PaddleOCR or Surya) to process uploaded scanned receipts, disputed damage photos, and police FIR reports dynamically.
3. **Session State & Multi-Turn Slot Filling**:
   - Maintain Redis-backed conversational state so that if a customer says "cancel it", the assistant prompts: "Are you referring to your upcoming booking B-0001 for tomorrow?" with an interactive confirmation button.
4. **Interactive Dispute & Waiver Workflow**:
   - Allow support agents to trigger authorized claim waivers or refund approvals directly through audited tool calls.
