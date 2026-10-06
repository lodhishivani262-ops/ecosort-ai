# 🌱 EcoSort AI — Household Waste Segregation Assistant

[![Live Web App](https://img.shields.io/badge/Live%20Demo-Vercel-success?style=for-the-badge&logo=vercel)](https://ecosort-ai-neon.vercel.app)
[![Backend Status](https://img.shields.io/badge/API-Render-black?style=for-the-badge&logo=render)](https://ecosort-ai-j8b8.onrender.com/health)
[![Database](https://img.shields.io/badge/Database-Neon%20Postgres-00E599?style=for-the-badge&logo=postgresql)](https://neon.tech)
[![AI Perception](https://img.shields.io/badge/AI-Google%20Gemini-blue?style=for-the-badge&logo=google)](https://ai.google.dev)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![React 19](https://img.shields.io/badge/Frontend-React%2019%20+%20Vite-61DAFB?style=for-the-badge&logo=react)](https://react.dev)
[![SDG 12](https://img.shields.io/badge/UN%20SDG-12%3A%20Responsible%20Consumption-DDA63A?style=for-the-badge)](https://sdgs.un.org/goals/goal12)

> **"Identify it. Sort it. Dispose responsibly."**  
> An intelligent, safety-first web application designed to guide households in responsible waste segregation, recycling preparation, and hazardous material management.

---

## 🔗 Live Deployments

* **🌐 Public Web Application**: [https://ecosort-ai-neon.vercel.app](https://ecosort-ai-neon.vercel.app)
* **⚡ FastAPI Production Backend**: [https://ecosort-ai-j8b8.onrender.com](https://ecosort-ai-j8b8.onrender.com)
* **🩺 Backend Health Probe**: [https://ecosort-ai-j8b8.onrender.com/health](https://ecosort-ai-j8b8.onrender.com/health)

---

## 📌 Project Overview

Household waste segregation is often hindered by confusion over composite materials, contamination guidelines (e.g. greasy pizza boxes), and dangerous household items (batteries, needles, broken glass). 

**EcoSort AI** bridges this gap using a **hybrid intelligence architecture**:
1. **Multimodal AI Perception**: Uses Google Gemini to objectively detect the item, material properties, and physical condition.
2. **Deterministic Rule Engine**: Evaluates perception against strict, audited waste segregation and safety rules. **No LLM hallucination in disposal guidance.**

---

## 🏛️ System Architecture

```text
       [ User Browser ] (Desktop / Mobile)
               │
               ▼ HTTPS
  ┌─────────────────────────┐
  │   Vercel Edge CDN       │  React 19 + TypeScript + Vite
  │   (ecosort-ai-neon)     │  Responsive Dark/Light UI
  └────────────┬────────────┘
               │ REST API
               ▼ HTTPS
  ┌─────────────────────────┐
  │   Render Web Service    │  FastAPI (Python 3.11/3.13)
  │   (ecosort-ai-j8b8)     │  Rate Limiting • Magic-Byte Validation
  └─────┬──────────────┬────┘
        │              │
        ▼              ▼
┌──────────────┐ ┌─────────────────────────┐
│ Google Gemini│ │   Neon Serverless DB    │
│ Perception   │ │   PostgreSQL Storage    │
│ (Multimodal) │ │   Audit & Feedback Logs │
└──────┬───────┘ └─────────────────────────┘
       │
       ▼
┌─────────────────────────┐
│ Deterministic EcoSort   │
│ Rule & Safety Engine    │  100% Deterministic Guardrails
└─────────────────────────┘
```

---

## ✨ Key Features

* **📷 Dual Input Options**:
  * Real-time device camera integration (WebRTC) with camera-permission error handling.
  * Image upload supporting JPEG, PNG, and WebP (strict magic-byte file validation, 5MB limit).
  * Natural language text descriptions (e.g., *"crushed aluminum soda can"*, *"broken mirror shards"*).
* **🛡️ Priority Safety Guardrails**:
  * Immediate safety overrides for batteries (fire hazard), medical sharps (biohazard), pressurized aerosols (explosion hazard), and broken glass (puncture hazard).
* **♻️ Contamination-Aware Logic**:
  * Detects degraded porous materials (e.g., greasy pizza boxes routed away from clean paper streams).
  * Detects multi-layer composite packaging (e.g., metallized chip bags routed to dry waste).
* **🔒 Privacy & Zero-PII Policy**:
  * **0 raw images stored**: Classification images are processed in-memory and discarded immediately.
  * History is scoped to anonymous client sessions (`X-Session-ID`) — zero user accounts or cross-session tracking.
  * Automated 30-day data retention pruning.
* **🌙 Thoughtful UI/UX**:
  * Custom eco-themed Dark and Light modes persisted in `localStorage`.
  * Mobile-responsive bottom navigation bar and desktop sidebar.
  * Loading skeleton animations and comprehensive error fallbacks.

---

## 🛠️ Tech Stack

| Tier | Technology | Purpose |
| :--- | :--- | :--- |
| **Frontend** | React 19, TypeScript, Vite 6 | Fast client-side SPA with zero runtime overhead |
| **Styling** | Vanilla CSS Design System | Custom eco-palette, smooth transitions, dark/light themes |
| **Icons** | Lucide React | Clean, line-art SVG icons |
| **Backend** | FastAPI, Uvicorn, Pydantic v2 | High-throughput asynchronous ASGI REST API |
| **Database** | PostgreSQL (Neon.tech), SQLAlchemy 2.0 | Resilient serverless relational storage with pre-ping pooling |
| **Migrations**| Alembic | Automated schema migration tracking |
| **AI Perception**| Google GenAI SDK (`gemini-3.5-flash`) | Multimodal object, material, and condition identification |
| **Security** | SlowAPI, Magic-byte inspection | Rate limiting (10 req/min), PE binary blocking, CSP & security headers |
| **Hosting** | Vercel (Frontend) + Render (Backend) | 100% Free production infrastructure with global HTTPS |

---

## 🚀 Local Development Setup

### 1. Clone Repository
```bash
git clone https://github.com/lodhishivani262-ops/ecosort-ai.git
cd ecosort-ai
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
# Edit .env and insert your GEMINI_API_KEY from Google AI Studio
uvicorn app.main:app --reload --port 8000
```
Backend will be available at: `http://localhost:8000`  
Interactive API docs at: `http://localhost:8000/docs`

### 3. Frontend Setup
```bash
cd ../frontend
npm install
npm run dev
```
Frontend will be available at: `http://localhost:5173`

---

## 🧪 Testing & Verification

The backend includes a comprehensive pytest suite with **96 tests** (100% pass rate):

```bash
cd backend
pytest tests -v
```

* `test_health.py`: Liveness probes, database connectivity, and security headers.
* `test_file_validation.py`: Magic bytes (JPEG/PNG/WebP), size boundaries (5MB), and executable blocking.
* `test_ai_service.py`: Multimodal perception, timeout handling, retry backoff, and secret sanitization.
* `test_rule_engine.py`: Deterministic categorization, safety overrides, composite packaging, and contamination handling.
* `test_classify.py`: Unified/dedicated endpoint contracts, request ID tracking, and database resilience.
* `test_database_and_feedback.py`: Session history isolation, rating boundaries, and retention pruning.

---

## 📡 Core API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Cloud deployment liveness probe |
| `GET` | `/api/v1/health` | Comprehensive health check with DB connectivity ping |
| `POST`| `/api/v1/classify` | Unified multimodal waste classification (Image or Text) |
| `POST`| `/api/v1/feedback` | User rating (1–5) and feedback submission |
| `GET` | `/api/v1/history` | Anonymous session-isolated classification history |
| `GET` | `/api/v1/metrics` | Protected summary metrics (Requires `X-Admin-Key`) |

---

## 📜 Environmental Impact & SDG 12

EcoSort AI directly supports **United Nations Sustainable Development Goal 12: Responsible Consumption and Production**:
* **Target 12.5**: Substantially reduce waste generation through prevention, reduction, recycling, and reuse.
* **Target 12.4**: Achieve environmentally sound management of chemicals and all wastes throughout their life cycle to minimize adverse impacts on human health and the environment.

---

## 📄 License
This project is open-source under the **MIT License**.
