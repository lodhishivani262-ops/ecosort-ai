# EcoSort AI — Backend API, AI Perception Layer, Rule Engine & Database Layer

> **Tagline:** *Identify it. Sort it. Dispose responsibly.*  
> **Global Alignment:** UN Sustainable Development Goal 12 (*Responsible Consumption & Production*)  
> **Current Stage:** Stage 5 — Database, History & User Feedback Layer

---

## 1. What is EcoSort AI?

**EcoSort AI** is an AI-assisted household waste segregation assistant designed to provide actionable waste disposal guidance. Instead of merely labeling waste objects, EcoSort AI identifies the item, evaluates its physical condition and cleanliness (e.g., food contamination or hazardous contents), and delivers step-by-step preparation and segregation instructions tailored to household waste streams.

> **Foundational Architectural Principle:**  
> **The AI perception layer acts purely as sensory observation (answering: "What appears to be in this image or text?").**  
> **The EcoSort Rule Engine is 100% deterministic code that evaluates those observations to produce the final category, preparation steps, safety warnings, and disposal route.**  
> **The Database Layer stores structured audit records and user feedback. Uploaded images are NEVER stored in the database.**

---

## 2. End-to-End Pipeline Architecture

```
User (Image or Text Query)
           │
           ▼
[ FastAPI Endpoint Layer ]
 (MIME validation, 5MB bounds, Rate limiting, Request-ID tracing)
           │
           ▼
[ AI Perception Layer (Stage 3) ]
 (Multimodal Google Gemini / Mock Provider)
           │
           ▼
[ Structured WastePerception ]
 (item_name, material, condition, contamination, visual_clues, confidence, is_safety_sensitive)
           │
           ▼
[ EcoSort Deterministic Rule Engine (Stage 4) ]
   ├── Level 1: Safety & Hazard Guardrail Overrides
   ├── Level 2: Unknown & Ambiguous Item Fallback
   ├── Level 3: E-Waste & Electronics Routing
   ├── Level 4: Sanitary & Bio-Hygiene Routing
   ├── Level 5: Organic & Biodegradable Routing
   ├── Level 6: Intact Glass Routing
   ├── Level 7: Recyclable Materials & Contamination Degradation Rules
   └── Level 8: General Dry Waste Default
           │
           ▼
[ Actionable WasteRecommendation ]
 (category, preparation_steps, disposal_guidance, warnings, confidence, reason, uncertainty_reason)
           │
           ├──────────────────────────────┐
           ▼                              ▼
[ Resilient Audit Service (Stage 5) ]   [ User Response ]
 (Logs structured metadata to DB;        (Combined ClassificationResultResponse)
  Failures NEVER impact response)
           │
           ▼
[ SQLAlchemy ORM + SQLite/PostgreSQL ]
 (classification_records, feedback)
```

---

## 3. Database Architecture & Models (Stage 5)

EcoSort AI uses a clean repository-pattern database architecture:
`API Layer` → `Service Layer` → `Repository Layer` → `SQLAlchemy ORM` → `Database`

### Table: `classification_records`
Stores structured audit metadata for every completed classification request without storing user images.

| Field | Type | Modifiers | Description |
| :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | Primary Key, Autoincrement | Record internal surrogate key |
| `request_id` | `VARCHAR(36)` | Unique, Indexed, Non-Null | UUID correlation tracing ID |
| `session_id` | `VARCHAR(64)` | Indexed, Nullable | Anonymous client session identifier |
| `created_at` | `TIMESTAMPTZ`| Indexed, Non-Null | UTC timestamp of classification event |
| `input_type` | `VARCHAR(10)` | Non-Null | Input modality (`IMAGE` or `TEXT`) |
| `item_name` | `VARCHAR(255)`| Non-Null | Name of identified waste object |
| `material` | `VARCHAR(100)`| Non-Null | Physical material identified |
| `condition` | `VARCHAR(100)`| Non-Null | Physical state / cleanliness |
| `contamination` | `VARCHAR(20)` | Non-Null | Contamination level (`NONE` to `HIGH`, `UNKNOWN`) |
| `ai_confidence` | `VARCHAR(10)` | Non-Null | AI perception confidence (`HIGH`, `MEDIUM`, `LOW`) |
| `category` | `VARCHAR(50)` | Indexed, Non-Null | One of 8 controlled waste categories |
| `recommendation_confidence`| `VARCHAR(10)`| Non-Null | Recommendation confidence level |
| `warning_count` | `INTEGER` | Default 0 | Number of safety warnings attached |
| `processing_time_ms`| `INTEGER`| Default 0 | Pipeline processing duration |
| `status` | `VARCHAR(20)` | Indexed, Non-Null | Operational status (`SUCCESS` or `FAILED`) |
| `error_message` | `VARCHAR(500)`| Nullable | Failure reason if status is `FAILED` |

### Table: `feedback`
Stores user satisfaction ratings and helpfulness reviews linked to a classification request.

| Field | Type | Modifiers | Description |
| :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | Primary Key, Autoincrement | Record internal surrogate key |
| `request_id` | `VARCHAR(36)` | ForeignKey, Indexed, Non-Null | Associated `classification_records.request_id` |
| `rating` | `INTEGER` | Nullable, Check (1-5) | Optional rating strictly bounded from 1 to 5 |
| `feedback_type` | `VARCHAR(50)` | Non-Null | `HELPFUL`, `NOT_HELPFUL`, `INCORRECT_CATEGORY`, etc. |
| `comment` | `VARCHAR(500)`| Nullable | Optional user remark (sanitized, max 500 chars) |
| `created_at` | `TIMESTAMPTZ`| Indexed, Non-Null | UTC timestamp of feedback submission |

### Index Strategy & Rationale
* `request_id`: Unique index on classifications and standard index on feedback for constant-time correlation lookups and joins.
* `session_id`: Index for efficient anonymous user history retrieval without scanning the entire table.
* `created_at`: Index on both tables for fast time-series aggregation, dashboard metrics, and privacy retention purges.
* `category`: Index for rapid category distribution breakdown without full table scans.
* `status`: Index for fast operational monitoring and success/failure rate calculations.

---

## 4. Privacy-First Principles & Policies

1. **Strict NO Image Storage Policy:**  
   Uploaded image bytes are parsed exclusively in temporary memory buffers (`UploadFile.read()`), sent to the AI perception provider over outbound TLS, and immediately dereferenced for Python garbage collection. **No column in the database stores image binaries, and no image URLs are persisted.**
2. **Anonymous Usage & No Forced Accounts:**  
   EcoSort AI does not require user accounts, email addresses, phone numbers, or passwords.
3. **Session-Scoped History Isolation:**  
   `GET /api/v1/history` requires an explicit anonymous `session_id` (via query param or `X-Session-ID` header). It never exposes cross-session records or global history to public callers.
4. **Data Retention Strategy:**  
   Records are subject to a configurable retention policy (`DATA_RETENTION_DAYS`, default 90 days). The repository includes a `delete_older_than(days)` maintenance method to purge expired records.
5. **Database Failure Resilience:**  
   If the database connection is interrupted or storage encounters errors during classification, the failure is logged internally and **the user's classification result is still returned safely**. Analytics persistence never impedes user guidance.

---

## 5. Database Migrations (Alembic)

Database schema evolution is managed through [Alembic](https://alembic.sqlalchemy.org/):

```bash
# Apply pending migrations to the database
alembic upgrade head

# Roll back the most recent migration
alembic downgrade -1

# Generate a new migration script following model changes
alembic revision --autogenerate -m "describe_changes"
```

Migration scripts live in [`app/db/migrations/versions/`](file:///d:/EcoSort%20AI/backend/app/db/migrations/versions/). Production deployments execute `alembic upgrade head` during release phases.

---

## 6. Technology Stack

* **Language:** Python 3.11+
* **Web Framework:** [FastAPI](https://fastapi.tiangolo.com/) (Asynchronous ASGI)
* **Database ORM:** [SQLAlchemy 2.0](https://www.sqlalchemy.org/)
* **Database Engines:** PostgreSQL (Production) / SQLite (Local Development)
* **Database Driver:** `psycopg` (PostgreSQL) / `aiosqlite` & standard `sqlite3`
* **Schema Migrations:** [Alembic](https://alembic.sqlalchemy.org/)
* **AI Provider:** [Google GenAI SDK](https://github.com/googleapis/python-genai) (`google-genai` >= 2.28.0)
* **Validation:** [Pydantic v2](https://docs.pydantic.dev/latest/) & [pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
* **Rate Limiting:** [SlowAPI](https://github.com/laurents/slowapi)
* **Testing:** [pytest](https://docs.pytest.org/), `pytest-anyio`, & [HTTPX](https://www.python-httpx.org/)

---

## 7. Folder Structure

```
backend/
├── alembic.ini                         # Alembic database migration configuration
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── router.py               # API v1 Central Router
│   │       └── endpoints/
│   │           ├── health.py           # Health check endpoints (/health)
│   │           ├── classify.py         # Perception + Rule Engine + Audit logging
│   │           ├── feedback.py         # User feedback endpoint (POST /feedback)
│   │           ├── metrics.py          # Aggregated analytics (GET /metrics)
│   │           └── history.py          # Anonymous history endpoint (GET /history)
│   ├── core/
│   │   ├── config.py                   # Pydantic BaseSettings (.env loader)
│   │   ├── logging.py                  # Structured logging with request tracing
│   │   ├── rate_limit.py               # SlowAPI limiter & 429 handler
│   │   └── security.py                 # Security headers & Request-ID middleware
│   ├── db/
│   │   ├── __init__.py
│   │   ├── base.py                     # SQLAlchemy DeclarativeBase
│   │   ├── database.py                 # Engine, SessionLocal & get_db dependency
│   │   ├── models.py                   # ClassificationRecord & Feedback ORM models
│   │   └── migrations/                 # Alembic migration scripts and env.py
│   │       └── versions/
│   │           └── 860eec298150_create_classification_and_feedback_.py
│   ├── repositories/                   # Data access repository layer
│   │   ├── __init__.py
│   │   ├── classification_repository.py
│   │   └── feedback_repository.py
│   ├── rules/                          # Stage 4 Deterministic Rule Engine
│   │   ├── __init__.py
│   │   ├── categories.py               # Re-exports WasteCategory enum
│   │   ├── material_rules.py           # Keyword taxonomies & porous material logic
│   │   ├── safety_rules.py             # Hazard & safety override engine
│   │   ├── contamination_rules.py      # Porous vs non-porous contamination evaluator
│   │   └── rule_engine.py              # Central EcoSortRuleEngine 8-tier hierarchy
│   ├── schemas/                        # Pydantic validation & response schemas
│   │   ├── common.py                   # ErrorDetail, StandardResponse envelopes
│   │   ├── classification.py           # WastePerception, WasteRecommendation & Result
│   │   ├── feedback.py                 # FeedbackCreate, FeedbackResponse
│   │   ├── metrics.py                  # MetricsResponse, CategoryBreakdown
│   │   └── history.py                  # HistoryResponse, ClassificationHistoryItem
│   ├── services/                       # Business logic services
│   │   ├── ai_service.py               # GeminiAIService, MockAIService & prompt
│   │   ├── audit_service.py            # Resilient classification audit logging
│   │   ├── feedback_service.py         # Feedback submission & duplicate validation
│   │   └── metrics_service.py          # Metrics computation service
│   ├── utils/
│   │   ├── file_validation.py          # Magic-byte validation & MIME security checks
│   └── main.py                         # FastAPI application entrypoint
├── tests/
│   ├── conftest.py                     # Pytest fixtures & isolated in-memory test DB
│   ├── test_ai_service.py              # AI perception layer tests
│   ├── test_classify.py                # End-to-end classification API tests
│   ├── test_database_and_feedback.py   # 23 tests for DB, feedback, history & metrics
│   ├── test_file_validation.py         # Magic byte & file validation tests
│   ├── test_health.py                  # Health check & security header tests
│   └── test_rule_engine.py             # 19 unit tests for Stage 4 Rule Engine
├── .env.example
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## 8. API Specification: Key Endpoints

### 1. Classification Endpoint: `POST /api/v1/classify`
Processes image or text, applies rules, and resiliently saves audit record:
* **Headers:** `X-Session-ID: <anonymous-session-uuid>` (optional)
* **Response:** Contains `request_id`, `perception`, `recommendation`.

### 2. User Feedback Endpoint: `POST /api/v1/feedback`
Submits user helpfulness reviews linked to a prior classification:
* **Rate Limit:** `20/minute`
* **Request Body:**
```json
{
  "request_id": "8f87e5b3-34e8-46c5-a22b-47e1d51a61c3",
  "rating": 5,
  "feedback_type": "HELPFUL",
  "comment": "The rinsing instructions were very clear."
}
```
* **Success Response (201 Created):**
```json
{
  "success": true,
  "message": "Thank you for your feedback.",
  "request_id": "8f87e5b3-34e8-46c5-a22b-47e1d51a61c3",
  "created_at": "2026-10-05T07:50:00Z"
}
```
* **Conflict (409 Conflict):** If feedback for this `request_id` was already submitted.
* **Not Found (404 Not Found):** If `request_id` does not match an existing classification.

### 3. Anonymous Session History Endpoint: `GET /api/v1/history`
Retrieves past classifications for an anonymous user session without leaking other users' data:
* **Query Params / Header:** `?session_id=<uuid>` or `X-Session-ID: <uuid>`
* **Response (200 OK):**
```json
{
  "session_id": "sess-abc-123",
  "total": 1,
  "items": [
    {
      "request_id": "8f87e5b3-34e8-46c5-a22b-47e1d51a61c3",
      "created_at": "2026-10-05T07:50:00Z",
      "input_type": "TEXT",
      "item_name": "plastic food container",
      "material": "plastic",
      "condition": "used with food residue",
      "contamination": "HIGH",
      "ai_confidence": "HIGH",
      "category": "RECYCLABLE",
      "recommendation_confidence": "HIGH",
      "warning_count": 1,
      "processing_time_ms": 120,
      "status": "SUCCESS"
    }
  ]
}
```

### 4. Aggregated Metrics Endpoint: `GET /api/v1/metrics`
Internal/admin endpoint for analytical monitoring:
* **Header (if configured):** `X-Admin-API-Key: <key>`
* **Response (200 OK):**
```json
{
  "total_classifications": 120,
  "successful_classifications": 114,
  "failed_classifications": 6,
  "average_processing_time_ms": 312.5,
  "low_confidence_percentage": 8.3,
  "categories": [
    { "category": "RECYCLABLE", "count": 65, "percentage": 54.2 },
    { "category": "ORGANIC / WET WASTE", "count": 30, "percentage": 25.0 },
    { "category": "HAZARDOUS / SPECIAL HANDLING", "count": 12, "percentage": 10.0 },
    { "category": "GLASS", "count": 8, "percentage": 6.7 },
    { "category": "UNKNOWN / UNCLASSIFIED", "count": 5, "percentage": 4.2 }
  ],
  "feedback": {
    "total_feedback": 45,
    "helpful_count": 40,
    "not_helpful_count": 5,
    "helpful_percentage": 88.9,
    "average_rating": 4.6,
    "type_breakdown": {
      "HELPFUL": 40,
      "NOT_HELPFUL": 3,
      "UNCLEAR_GUIDANCE": 2
    }
  }
}
```

---

## 9. Automated Testing (76 Tests Passing)

All tests execute fully offline with an isolated in-memory SQLite database, mock AI service, and clean table resets:

```bash
pytest tests -v
```

```
tests/test_ai_service.py              11 passed
tests/test_classify.py                13 passed
tests/test_database_and_feedback.py   23 passed
tests/test_file_validation.py          7 passed
tests/test_health.py                   3 passed
tests/test_rule_engine.py             19 passed
======================= 76 passed in 4.41s =======================
```

---

## 10. Environment Variables

| Variable | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `DATABASE_URL` | `str` | `sqlite:///./ecosort.db` | Database connection URI (PostgreSQL or SQLite) |
| `DATA_RETENTION_DAYS` | `int` | `90` | Automatic retention threshold for audit records |
| `METRICS_API_KEY` | `str` | `""` | Optional access key protecting `GET /api/v1/metrics` |
| `AI_PROVIDER` | `str` | `gemini` | Multimodal AI perception provider (`gemini` or `mock`) |
| `AI_MODEL` | `str` | `gemini-2.5-flash` | Multimodal model identifier |
| `GEMINI_API_KEY` | `str` | `""` | Google Gemini API key |
| `MAX_UPLOAD_SIZE_MB` | `int` | `5` | Maximum image upload file size |
| `RATE_LIMIT` | `str` | `10/minute` | Rate limit threshold per IP for classification endpoints |
