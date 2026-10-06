# EcoSort AI — Frontend & Modern Interactive Dashboard

> **AI-Based Household Waste Segregation Assistant**  
> *"Identify it. Sort it. Dispose responsibly."*  
> Supporting **UN SDG 12: Responsible Consumption & Production**

---

## 1. Overview

The **EcoSort AI** frontend is a high-performance, responsive single-page application built with **React**, **TypeScript**, and **Vite**. It provides a modern, intuitive user interface that seamlessly interfaces with the EcoSort AI FastAPI backend.

### Strict Architectural Boundaries
- **Zero Business Logic in Frontend**: The frontend handles only rendering, layout, interaction states, and API communication. All visual perception, material analysis, contamination assessment, deterministic rule engine evaluation, and safety overrides remain strictly inside the backend.
- **Privacy & Zero Image Storage**: Uploaded waste photos are held only in memory during upload and analysis. No images are saved to local storage, cookies, or backend persistent databases.
- **Theme Consistency**: Permanent brand accent of **EcoSort Green (`#10b981`)** across both Dark Mode (default) and Light Mode.

---

## 2. Technology Stack

- **Framework**: React 19 + TypeScript
- **Bundler & Tooling**: Vite 8
- **Icons**: Lucide React
- **Styling**: Modern CSS custom properties (design tokens, glassmorphism, responsive CSS grid/flexbox)
- **Zero Heavy Frameworks**: No Tailwind bloat, no complex state management libraries (Redux/Zustand), no animation bloat. Fast and clean.

---

## 3. Directory Structure

```
frontend/
├── index.html                  # EcoSort AI branding & meta tags
├── package.json                # Scripts & dependencies
├── tsconfig.json               # TypeScript compiler config
├── vite.config.ts              # Vite config with /api & /health dev proxy
├── .env.example                # Base URL configuration
└── src/
    ├── main.tsx                # App entrypoint
    ├── App.tsx                 # App layout shell, navigation & theme state
    ├── index.css               # Global typography, layout reset, scrollbars
    ├── types/
    │   ├── api.ts              # Type-safe contracts matching FastAPI models
    │   └── navigation.ts       # Navigation tab identifiers
    ├── utils/
    │   ├── session.ts          # Anonymous session ID generation & persistence
    │   └── formatters.ts       # Badge color mappings, relative time & styling
    ├── styles/
    │   └── theme.css           # Dark (default) and Light CSS design tokens
    ├── api/
    │   ├── client.ts           # Central fetch wrapper with X-Session-ID header
    │   ├── classify.ts         # Multimodal waste classification (image / text)
    │   ├── feedback.ts         # User ratings & issue reporting
    │   ├── history.ts          # Session-scoped classification history
    │   ├── metrics.ts          # Aggregated application analytics & KPI metrics
    │   └── health.ts           # Backend liveness & connectivity probe
    ├── components/
    │   ├── common/
    │   │   ├── Badge.tsx       # Category, Confidence & Contamination badges
    │   │   ├── Button.tsx      # Consistent styled buttons with loading states
    │   │   ├── Card.tsx        # Container card with surface tokens & borders
    │   │   └── Modal.tsx       # Accessible dialog modal
    │   ├── layout/
    │   │   ├── Topbar.tsx      # Header with branding, theme toggle, mobile toggle
    │   │   ├── Sidebar.tsx     # Desktop sidebar with navigation & '+ New Scan'
    │   │   └── MobileNav.tsx   # Mobile fixed bottom tab bar
    │   └── analyze/
    │       ├── ImageUploader.tsx # Drag-and-drop, camera trigger, preview & size check
    │       ├── TextInput.tsx   # Text description input with character counter
    │       ├── LoadingState.tsx# Multi-step progress animation indicator
    │       ├── ResultCard.tsx  # Perception + rule recommendation display
    │       └── FeedbackWidget.tsx# Helpful/Not helpful rating & issue submission
    └── pages/
        ├── DashboardPage.tsx   # Overview, quick CTA, KPI cards, recent scans
        ├── AnalyzePage.tsx     # Multimodal analysis workspace & result card
        ├── HistoryPage.tsx     # Anonymous session history list & detail viewer
        ├── InsightsPage.tsx    # Category distributions, KPI cards & ratings
        └── SettingsPage.tsx    # Appearance toggle, token reset & health probe
```

---

## 4. Key Pages & Features

1. **Dashboard Overview (`/`)**
   - Welcome banner with SDG 12 context and quick '+ New Scan' CTA.
   - Real-time aggregated KPI counters (total scans, satisfaction rate, average latency, safety overrides).
   - Recent activity feed scoped to the current anonymous session.
   - Quick reference guide to 8 municipal waste streams.

2. **Waste Analyzer Workspace**
   - Seamless toggle between **Photo / Camera** and **Text Description** modes.
   - Drag-and-drop image upload with live client preview, file-type validation, and size constraints (10MB max).
   - Instant camera capture support on mobile devices via `capture="environment"`.
   - Polished analysis progress state displaying the dual-layer pipeline (Perception → Rule Engine).
   - Explanatory Result Card with item name, material, condition, contamination level, preparation steps, disposal guidance, and safety warnings.

3. **User Feedback Integration**
   - Simple thumbs-up / thumbs-down helpfulness rating tied to each classification ID.
   - Detailed issue tagging for incorrect categories, item misidentifications, or unclear instructions.

4. **Anonymous Session History**
   - View past classifications made during the current browser session.
   - View detailed parameters (material, condition, contamination, confidence, latency) in a modal.
   - One-click "Reset Session" button to detach previous history and generate a new anonymous token.

5. **Analytics & Insights**
   - Real-time waste stream distribution breakdown with visual progress bars.
   - Feedback metrics (average rating, total submissions, issue type breakdown).
   - Low confidence detection percentage indicator.

6. **Settings & Privacy**
   - Theme toggle: **Dark Mode (Default)** and **Light Mode**, both retaining permanent EcoSort Green (`#10b981`).
   - Copy or regenerate anonymous session tokens.
   - Live backend API connectivity and latency diagnostic probe (`/health`).
   - Clear disclosure of privacy guarantees (zero image retention, deterministic rules).

---

## 5. Development & Running

### Prerequisites
- Node.js 18+ (tested on Node 22+)
- Running EcoSort AI FastAPI Backend (default: `http://127.0.0.1:8000`)

### Installation
```bash
cd frontend
npm install
```

### Local Development Server
```bash
npm run dev
```
The application will launch at `http://localhost:5173/`.  
Vite is pre-configured with a reverse proxy routing `/api` and `/health` requests to `http://127.0.0.1:8000`.

### Production Build
```bash
npm run build
```
Generates optimized static assets in `frontend/dist/`.

---

## 6. Environment Variables

Create `.env` in `frontend/` (optional for local dev as Vite proxy is enabled):
```env
# Optional: In production, configure the public backend URL if hosted separately
VITE_API_BASE_URL=
```
