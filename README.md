# 🎯 DE-INTEL: Enterprise Decision Intelligence Platform

[![Google Cloud Platform](https://img.shields.io/badge/Google_Cloud_Platform-4285F4?style=for-the-badge&logo=google-cloud&logoColor=white)](https://cloud.google.com/)
[![Vertex AI](https://img.shields.io/badge/Vertex_AI-00C4CC?style=for-the-badge&logo=google-cloud&logoColor=white)](https://cloud.google.com/vertex-ai)
[![BigQuery](https://img.shields.io/badge/BigQuery-669DF2?style=for-the-badge&logo=google-cloud&logoColor=white)](https://cloud.google.com/bigquery)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)

> **Submission Project for the Google Cloud Gen AI Academy APAC 2026 Cohort 2**
> *Moving organizations from static, reactive dashboards to autonomous, AI-driven decision-making.*

**DE-INTEL** is a cloud-native, stateless, and fully secure "Decision Intelligence" web application. It intercepts today's real-time global news events, performs high-dimensional historical semantic alignment, models multi-domain cascading risks, and delivers actionable strategic foresight with probabilistic recommendations for executive leaders.

---

## 🏗️ System Architecture

Rather than executing standard RAG loops, **DE-INTEL** implements an **asynchronous multi-stage agentic reasoning pipeline** that operates fully keyless in production:

```text
[Streamlit Frontend] ──(gRPC / WebSocket Session)──> [FastAPI Backend]
                                                          │
             ┌────────────────────────────────────────────┼────────────────────────────────────────────┐
             ▼                                            ▼                                            ▼
     [Vertex AI SDK]                              [BigQuery Cache]                          [BigQuery Vector Search]
  - Gemini 2.5 Flash                           - Stateless Cache Tables                   - HNSW Cosine Similarity Match
  - Google Search Grounding                    - Zero Ephemeral Disk Dependency           - ML.DISTANCE over Precedents
  - text-embedding-005
🚀 Key Technical Highlights
Google Search Grounding (Live-news Layer): Leverages Vertex AI’s Gemini 2.5 Flash integrated with live Google Search indices to discover today's breaking events with zero hallucinations.
SQL-Native BigQuery Vector Search: Replaces local vector clients with BigQuery's native ML.DISTANCE function, executing sub-millisecond similarity matching over a database of 50 high-impact historical crises.
100% Stateless BigQuery Caching: Neutralizes container scale-to-zero data loss by storing all pipeline results, news items, and analysis states directly inside persistent BigQuery tables.
Keyless Zero-Trust IAM Security: Deployed fully keyless on Google Cloud Run using Application Default Credentials (ADC) [1]. Standard cloud service accounts assume role boundaries automatically, entirely eliminating static API key exposures.
Conversational Analyst Agent (Track 1): Features an interactive chatbot built into the dashboard, enabling executives to query and stress-test the loaded strategic reports on the fly.
🧭 Executive-First UX Design
Designed around executive scannability (under 10 seconds to absorb critical risk profiles):

Executive KPI Bar: Highlights overall threat percentage, critical target domain, historical alignment metrics, and model recommendation confidence at a glance.
Interactive Glassmorphism Dashboard: Compilation of multi-domain cascading risks with glowing indicators matching positive, mixed, and negative impacts.
"Then vs. Now" Comparative Grid: Displays modern disruptions side-by-side with historical analogues to minimize cognitive friction.
Three-Path Scenario Matrix: Structures corporate recommendations into clear Optimal, Standard, and Systemic Failure options.
📂 Repository Structure
decision_intelligence_platform/
│
├── backend/
│   ├── Dockerfile           # Backend container build
│   ├── main.py              # FastAPI Web Router and Endpoint Orchestrator
│   ├── models.py            # Pydantic v2 data contracts
│   ├── database.py          # BigQuery cloud-native stateless cache
│   ├── gemini_service.py    # Vertex AI SDK (Gemini 2.5 & text-embedding-005)
│   ├── bigquery_service.py  # BigQuery Vector Search (ML.DISTANCE engine)
│   └── briefing.py          # Dynamic glassmorphism HTML visualizer
│
├── frontend/
│   ├── Dockerfile           # Streamlit container build with Session Affinity
│   └── app.py               # Streamlit Executive Dashboard & Chat Interface
│
├── seed_historical_events_bq.py  # Vertex AI embedding & BigQuery data loader
├── requirements.txt         # Production-locked dependencies
├── .gitignore               # Multi-layer git ignore rules
└── README.md                # Comprehensive documentation
🛠️ Local Setup & Execution Guide
1. Authenticate with Google Cloud
Ensure your local environment is authenticated to communicate with your GCP Project resources:

# Log in to Google Cloud CLI
gcloud auth login

# Set up Application Default Credentials (ADC) for local development
gcloud auth application-default login

# Configure your active project ID
gcloud config set project YOUR_GCP_PROJECT_ID
2. Configure Local Environment Variables
Create a .env file in your root folder:

GCP_PROJECT_ID=your-actual-gcp-project-id
GCP_REGION=us-central1
BACKEND_URL=http://127.0.0.1:8000
3. Seed the BigQuery Database
Run the seeding script to compile historical events, generate embeddings using Vertex AI text-embedding-005, create the schema, and stream them into BigQuery:

python seed_historical_events_bq.py
4. Build and Run Local Containers
# Build Docker images
docker build -t de-intel-backend -f backend/Dockerfile .
docker build -t de-intel-frontend -f frontend/Dockerfile .

# Run Backend
docker run -p 8000:8080 --env-file .env de-intel-backend

# Run Frontend
docker run -p 8501:8080 --env-file .env de-intel-frontend
Open http://localhost:8501 in your browser to run the platform locally.

☁️ Google Cloud Run Deployment
Deploy your backend first to establish your API routing address:

Step 1: Deploy Backend Container
gcloud run deploy de-intel-backend \
    --source . \
    --port 8080 \
    --region us-central1 \
    --allow-unauthenticated \
    --set-env-vars="GCP_PROJECT_ID=YOUR_GCP_PROJECT_ID,GCP_REGION=us-central1"
Note down the generated Backend Service URL (e.g., https://de-intel-backend-xxxx.run.app).

Step 2: Deploy Frontend Streamlit Container
When deploying the frontend to Cloud Run, enable --session-affinity to ensure WebSockets stay mapped to the same container instance, preventing session drops:

gcloud run deploy de-intel-frontend \
    --source . \
    --port 8080 \
    --region us-central1 \
    --allow-unauthenticated \
    --session-affinity \
    --timeout=3600 \
    --set-env-vars="BACKEND_URL=https://de-intel-backend-xxxx.run.app,GCP_PROJECT_ID=YOUR_GCP_PROJECT_ID,GCP_REGION=us-central1"
🔐 Zero-Trust IAM Configuration
In production on Cloud Run, the services execute completely keyless. Ensure that your project's Default Compute Service Account (which Cloud Run uses) has the following roles assigned in the Google Cloud Console's IAM section:

Vertex AI User (roles/aiplatform.user) - Allows calls to Gemini 2.5 and Embeddings.
BigQuery Admin (roles/bigquery.admin) - Provides vector search and caching capabilities.
👥 Cohort 2 Submission Alignment
This project acts as an elite showcase for the APAC 2026 Cohort 2 evaluation:

Unified Analytics: Unifies real-time streaming web queries (Gemini grounding) with long-term structured historical data directly on BigQuery.
Autonomous Decisioning: Moves beyond traditional, passive charts by simulating operational impacts and defining probabilistic mitigation pathways.
Conversational AI (Track 1): Features a contextual agent that lets executives interrogate report findings through natural language.
