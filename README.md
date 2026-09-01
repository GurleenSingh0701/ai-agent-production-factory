# 🤖 AI Agent Production Factory

[![FastAPI](https://img.shields.io/badge/FastAPI-009485?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Blue?style=for-the-badge)](https://langchain-ai.github.io/langgraph/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker)](https://www.docker.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit)](https://streamlit.io/)
[![Langfuse](https://img.shields.io/badge/Langfuse-Observability-orange?style=for-the-badge)](https://langfuse.com/)

Welcome to the **AI Agent Production Factory**. This is not a collection of "AI wrappers," but a modular, enterprise-grade framework designed to build, deploy, and monitor autonomous AI agents. 

The goal of this project is to build **30 production-ready agents in 30 days**, focusing on reliability, observability, and scalability.

## 🚀 Completed Agents

### Day 1: Lead Qualification Agent
The first agent in the factory is the **Lead Qualification Agent**. It transforms a raw company URL and an Ideal Customer Profile (ICP) into a structured business decision.

**The Problem:** Sales teams waste 50% of their time on leads that don't fit their target profile. Manual research is slow and inconsistent.

**The Solution:** A multi-step agentic pipeline that:
1. **Scrapes** live web content from the company URL.
2. **Researches** the company's core product and business model.
3. **Evaluates** the fit against a specific ICP.
4. **Scores** the lead with a structured JSON output (0-100).

### Day 2: Email Triage & Draft Agent
The second agent is the **Email Triage & Draft Agent**, designed to act as an intelligent first-responder for high-volume inboxes.

**The Problem:** Sorting through hundreds of emails to identify urgent complaints versus sales inquiries is a manual bottleneck.

**The Solution:** A state-machine pipeline that:
1. **Triage:** Categorizes the email (Complaint, Sales, Support, Spam) and detects sentiment using `json_mode`.
2. **Prioritize:** Assigns a priority level (High, Medium, Low) based on content.
3. **Draft:** Applies a modular **Style Guide** (e.g., empathetic for complaints, enthusiastic for sales) to generate a professional response.
4. **Structured Output:** Returns a clean JSON object for seamless frontend rendering.

---

## 🏗️ Architecture

### 1. System Overview
The system is decoupled into a **Frontend (UI)** and a **Backend (API)**. It now includes a **Caching Layer** to reduce LLM latency and a **Centralized Logging** system for production debugging.

```mermaid
graph TD
    User((User)) -->|Interacts| UI[Streamlit Frontend]
    UI -->|REST API Call| API[FastAPI Backend]
    
    subgraph "Agent Engine"
        API -->|Invoke| LG[LangGraph State Machine]
        LG -->|Check Cache| RC[Redis Cache]
        RC -->|Miss| LLM[LiteLLM Wrapper]
        LG -->|Tool Call| SCR[Web Scraper]
    end
    
    subgraph "Infrastructure"
        LLM -->|Query| CloudLLM[Cloud Ollama / Gemini]
        LG -->|Logs/Traces| LF[Langfuse Observability]
        LG -->|System Logs| PL[Python Logger]
        RC -->|Store/Retrieve| Redis[Upstash Redis]
        LG -->|Vector Store| Neon[Neon Postgres/pgvector]
    end
```

### 2. Agent Logic Flow (LangGraph)
Unlike linear chains, these agents use a **State-Machine** to ensure each step is completed and validated before moving to the next.

**Example: Lead Gen Flow**
```mermaid
graph LR
    A[Input: URL + ICP] --> B(Scrape Website)
    B --> C(Research & Synthesize)
    C --> D(Evaluate Fit)
    D --> E(Structured Scoring)
    E --> F[Output: JSON Result]
    
    style B fill:#f9f,stroke:#333,stroke-width:2px
    style E fill:#bbf,stroke:#333,stroke-width:2px
```

**Example: Email Triage Flow**
```mermaid
graph LR
    A[Input: Raw Email] --> B(Triage: Category/Priority)
    B --> C(Apply Style Guide)
    C --> D(Draft Response)
    D --> E[Output: JSON Result]
    
    style B fill:#f9f,stroke:#333,stroke-width:2px
    style D fill:#bbf,stroke:#333,stroke-width:2px
```

---

## 🛠️ Technical Stack

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Orchestration** | `LangGraph` | Manages state and agentic loops for reliable execution. |
| **API Framework** | `FastAPI` | High-performance asynchronous API layer. |
| **LLM Gateway** | `LiteLLM` | Model-agnostic interface (Switch between Gemini/Ollama in 1 line). |
| **Observability** | `Langfuse` | Full-stack tracing, cost tracking, and latency monitoring. |
| **UI/Frontend** | `Streamlit` | Rapid deployment of professional AI interfaces. |
| **Data/Cache** | `Neon` / `Upstash` | Serverless Postgres (pgvector) and Redis for state/caching. |
| **Logging** | `Python Logging` | Centralized system logs for infrastructure health. |
| **Deployment** | `Docker` / `Render` | Containerized microservices for cloud portability. |

---

## ⚙️ Setup & Installation

### Prerequisites
- Docker & Docker Compose
- API Keys for Langfuse, Gemini/Ollama, Neon, and Upstash.

### Local Development
1. **Clone the repo:**
   ```bash
   git clone https://github.com/GurleenSingh0701/ai-agent-production-factory.git
   cd ai-agent-factory
   ```
2. **Configure Environment:**
   Create a `.env` file in the root:
   ```env
   DEFAULT_MODEL=gemini/gemini-1.5-flash
   GEMINI_API_KEY=your_key
   LANGFUSE_PUBLIC_KEY=your_key
   LANGFUSE_SECRET_KEY=your_key
   LANGFUSE_HOST=https://cloud.langfuse.com
   OLLAMA_API_BASE=https://your-cloud-ollama-url.com
   DATABASE_URL=postgresql://...
   REDIS_URL=redis://...
   ```
3. **Launch the Factory:**
   ```bash
   docker-compose up --build
   ```
4. **Access the UI:**
   Visit `http://localhost:8501`

---

## 📅 30-Day Roadmap
- [x] **Day 1: Lead Qualification Agent** (Scraping $\rightarrow$ Evaluation $\rightarrow$ Scoring)
- [x] **Day 2: Email Triage & Draft Agent** (Triage $\rightarrow$ Style Guide $\rightarrow$ Drafting)
- [ ] ... (More agents coming daily)

---

## 📩 Contact & Hire
I am building this factory to demonstrate the intersection of **Software Engineering** and **AI**. If you are looking for an AI Engineer who builds for reliability, observability, and scale, let's connect.

- **LinkedIn:** [https://www.linkedin.com/in/gurleen-singh-bhatia/]
- **Portfolio:** [https://gurleensingh1608-ai.lovable.app/]
- **Email:** [gurleensingh1608@gmail.com]