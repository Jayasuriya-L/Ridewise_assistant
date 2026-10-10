# RideWise Assist

**RideWise Assist** is an enterprise-grade AI concierge designed for **RideWise Mobility**. It enables customers and customer support agents to query operational rental data, verify booking status, review damage assessments, understand policy terms, and calculate refund eligibility and penalties with 100% mathematical and policy fidelity.

Developed for the **NeoStats AI Engineer Intern Hackathon 2026**.

---

## 1. Project Overview

RideWise Assist solves the challenge of combining:
1. **Live Operational Database Data**: Customer profiles, vehicle inventory, booking statuses, payment transactions, and damage reports stored in SQLite.
2. **Policy Documentation (5 Official Documents)**: Rental agreement terms, versioned cancellation & refund policies (v1 vs v2), late return and damage schedules, and EV user guidelines.
3. **Enterprise LLM Synthesis**: Integration with the NeoStats-hosted Azure OpenAI endpoint (`gpt-oss-120b`), utilizing deterministic calculations and factual grounding to eliminate hallucinations.
4. **Tenant Security & Access Control**: Rigid boundary enforcement ensuring customers cannot access, view, or speculate upon other customers' confidential records.

---

## 2. Architecture

```
                       +----------------------------------+
                       |   React + Vite + TS Frontend    |
                       |    (Role Switcher & Chat UI)     |
                       +----------------+-----------------+
                                        | (REST / JSON)
                                        v
                       +----------------------------------+
                       |      FastAPI Backend Server      |
                       +----------------+-----------------+
                                        |
      +------------------------+--------+------------------------+
      |                        |                                 |
      v                        v                                 v
+-------------+      +--------------------+            +-------------------+
|  auth.py    |      |  query_router.py   |            |   database.py     |
| Role & ID   |      | Intent Classifier  |            | Read-Only SQLite  |
| Validation  |      | Entity Extractor   |            | Parameterized SQL |
+-------------+      +---------+----------+            +---------+---------+
                               |                                 |
                               v                                 v
                     +--------------------+            +-------------------+
                     |policy_retrieval.py |            |   Deterministic   |
                     | 5 PDFs + Scanned   |            |    Calculation    |
                     | Schedule OCR       |            |      Engine       |
                     +---------+----------+            +---------+---------+
                               |                                 |
                               +----------------+----------------+
                                                |
                                                v
                               +---------------------------------+
                               |     NeoStats LLM Client (llm.py)|
                               |      Grounded Synthesis         |
                               +---------------------------------+
```

Full architecture specifications and request sequence diagrams are documented in [`docs/architecture.md`](file:///E:/policy_ai/ridewise-assist/docs/architecture.md).

---

## 3. Prerequisites

- **Python**: 3.10, 3.11, or 3.12 (Tested on Python 3.11.5)
- **Node.js**: v18.0.0 or above (Tested on Node v22.17.1)
- **Package Managers**: `pip` and `npm`

---

## 4. Installation & Setup

### A. Clone / Open Directory
Navigate to the `ridewise-assist` directory inside the workspace:
```bash
cd E:\policy_ai\ridewise-assist
```

### B. Backend Virtual Environment & Dependencies
```powershell
# Create virtual environment (if not already present)
python -m venv venv

# Activate virtual environment (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Install required Python dependencies
pip install -r backend/requirements.txt
```

### C. Frontend Dependencies
```bash
cd frontend
npm install
cd ..
```

---

## 5. Environment Configuration

Configuration is loaded from `.env` in the project root or backend directory. A template is provided in `.env.example`.

Create or inspect `.env`:
```env
# Backend Server Configuration
BACKEND_HOST=127.0.0.1
BACKEND_PORT=8000
FRONTEND_ORIGIN=http://localhost:5173

# SQLite Database Location (referencing supplied hackathon resources)
DATABASE_PATH=E:/policy_ai/hackathon_resources/ridewise.db

# Policy Documents Directory
POLICY_DIR=E:/policy_ai/hackathon_resources

# NeoStats LLM Credentials
OPENAI_ENDPOINT=https://neo-hackathon.services.ai.azure.com/openai/v1/
OPENAI_MODEL_NAME=gpt-oss-120b
OPENAI_DEPLOYMENT_NAME=Neo-Hackathon
OPENAI_API_KEY=your_hackathon_api_key_here
```

> **Security Note**: Never commit `.env` or API keys to Git. `.env` is listed in `.gitignore`.

---

## 6. Exact Commands to Run

### Run the Backend (FastAPI)
From the project root:
```powershell
$env:PYTHONPATH="E:\policy_ai\ridewise-assist\backend"
.\venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
The backend API will start at: `http://127.0.0.1:8000` (API docs available at `/docs`).

### Run the Frontend (React + Vite)
In a separate terminal:
```bash
cd E:\policy_ai\ridewise-assist\frontend
npm run dev
```
The application will be accessible at: `http://localhost:5173`.

---

## 7. Testing Instructions

Run the automated test suite covering health checks, SQLite database access, role access controls, cross-tenant isolation, policy versioning, and chat flows:

```powershell
cd E:\policy_ai\ridewise-assist\backend
$env:PYTHONPATH="E:\policy_ai\ridewise-assist\backend"
..\venv\Scripts\pytest.exe tests -v
```

### Key Test Scenarios Verified:
1. `test_health_check_endpoint`: Health endpoint reports database connectivity and indexed policy count.
2. `test_customer_lookup` & `test_customer_bookings`: Verifies actual SQLite queries return real data.
3. `test_customer_role_requires_customer_id`: Rejects customer requests missing IDs.
4. `test_customer_ownership_enforcement`: Asserts `CUST0001` cannot access records of `CUST0002` (403 Forbidden).
5. `test_policy_version_selection`: Validates that bookings before 1 July 2026 IST use Policy v1, and bookings on/after use Policy v2.
6. `test_chat_support_agent_access`: Validates Support Agent operational queries across any booking.

---

## 8. Known Limitations

1. **OCR Pre-Processing**: Scanned Annexures (such as Policy v2 signed refund schedule and Penalty Schedule tier benefits) are transcribed and indexed via supplementary text blocks. Full runtime dynamic OCR would require heavy Tesseract binaries.
2. **Read-Only Operations**: The system is designed strictly for assistance, inquiry, and audit. Direct modifications to bookings or payments are intentionally disallowed to maintain data integrity.
3. **LLM Connectivity**: In the event of network timeouts or Azure rate limits, the system provides direct database facts and policy references while gracefully reporting the LLM issue.
