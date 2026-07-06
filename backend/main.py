import json
import math
import asyncio
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from datetime import date
from models import (
    Article, RippleEffect, HistoricalEvent, HistoricalMatch, Recommendation,
    DomainBriefing, VisualBriefing, CompleteAnalysisReport
)
from database import (
    init_db, get_cached_headlines, set_cached_headlines,
    get_cached_analysis, set_cached_analysis
)
from gemini_service import GeminiService
from bigquery_service import BigQueryService
#from chroma_service import ChromaService
from datetime import datetime
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    init_db()
    yield
    # Shutdown logic (if any) can go here

app = FastAPI(
    title="News-Driven Decision Intelligence Platform API",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

gemini_service = GeminiService()
bigquery_service = BigQueryService()  # Core Vector Engine


def cosine_similarity(v1, v2):
    dot_product = sum(a * b for a, b in zip(v1, v2))
    magnitude_v1 = math.sqrt(sum(a * a for a in v1))
    magnitude_v2 = math.sqrt(sum(a * a for a in v2))
    if magnitude_v1 == 0 or magnitude_v2 == 0:
        return 0.0
    return dot_product / (magnitude_v1 * magnitude_v2)

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/news/headlines", response_model=List[Article])
async def get_headlines(category: str = Query(..., description="Spherical filter domain")):
    current_date = date.today().isoformat()
    cached = get_cached_headlines(current_date, category)
    if cached:
        return [Article(**item) for item in cached]
    
    try:
        headlines_data = await gemini_service.fetch_todays_headlines(category, current_date)
        set_cached_headlines(current_date, category, headlines_data)
        return [Article(**item) for item in headlines_data]
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to resolve grounded headlines for today: {str(e)}"
        )

@app.get("/news/article/{article_id}", response_model=CompleteAnalysisReport)
def get_complete_report(article_id: str):
    cached = get_cached_analysis(article_id)
    if not cached:
        raise HTTPException(status_code=404, detail="No analytical report parsed in active directory.")
    return CompleteAnalysisReport(**cached)

@app.post("/news/analyze")
async def analyze_news(req: Dict[str, Any]):
    article_dict = req.get("article")
    if not article_dict:
        raise HTTPException(status_code=400, detail="Target Article instance required.")
    
    article = Article(**article_dict)
    article_id = article.id
    
    cached = get_cached_analysis(article_id)
    if cached:
        return cached
        
    try:
        # Step 2: Extract Entities & Summary via Grounding
        scan_res = await gemini_service.deep_scan(article.title, article.url)
        entities = scan_res.get("entities", [])
        event_type = scan_res.get("event_type", "General")
        detailed_summary = scan_res.get("detailed_summary", "")
        
        # Step 3: Find Connected Events (Grounded Search)
        current_date = "2026-07-04"
        connected = await gemini_service.discover_connected_events(
            title=article.title,
            entities=entities,
            event_type=event_type,
            current_date=current_date
        )
        
        # Cross-check today's other cached headlines via Semantic Vector Similarity
        local_overlaps = []
            
        all_connected = connected.get("connected_events", []) + local_overlaps
        seen_titles = set()
        dedup_connected = []
        for c in all_connected:
            title_norm = c["title"].lower().strip()
            if title_norm not in seen_titles:
                seen_titles.add(title_norm)
                dedup_connected.append(c)
                
        article.entities = entities
        
        report_data = {
            "article": article.model_dump(),
            "entities": entities,
            "event_type": event_type,
            "detailed_summary": detailed_summary,
            "connected_events": dedup_connected,
            "ripple_effects": [],
            "historical_matches": [],
            "recommendations": []
        }
        
        set_cached_analysis(article_id, report_data)
        return report_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline Stage 1 analysis collapsed: {str(e)}")

@app.post("/ripple/predict")
async def predict_ripples(req: Dict[str, Any]):
    article_id = req.get("article_id")
    cached = get_cached_analysis(article_id)
    if not cached:
        raise HTTPException(status_code=404, detail="Cache directory state not verified.")
        
    if cached.get("ripple_effects"):
        return cached["ripple_effects"]
        
    try:
        ripples = await gemini_service.predict_ripple_effects(
            title=cached["article"]["title"],
            summary=cached["detailed_summary"],
            connected_events=cached["connected_events"]
        )
        
        ripple_list = ripples.get("ripple_effects", [])
        parsed_ripples = [RippleEffect(**r) for r in ripple_list]
        
        cached["ripple_effects"] = [r.model_dump() for r in parsed_ripples]
        set_cached_analysis(article_id, cached)
        return cached["ripple_effects"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ripple prediction core failure: {str(e)}")

@app.post("/history/similar")
async def find_similar_history(req: Dict[str, Any]):
    article_id = req.get("article_id")
    cached = get_cached_analysis(article_id)
    if not cached:
        raise HTTPException(status_code=404, detail="Cache directory state not verified.")
        
    if cached.get("historical_matches"):
        return cached["historical_matches"]
        
    try:
        # Get query vector via Vertex AI
        query_vector = await gemini_service.get_embedding(cached["detailed_summary"])
        # Query BigQuery Vector search
        matches = bigquery_service.query_similar_events(query_vector, n_results=4)
        cached["historical_matches"] = [
            {
                "historical_event": {
                    "id": m["id"],
                    "title": m["title"],
                    "date": m["date"],
                    "description": m["description"],
                    "sector": m["sector"],
                    "outcome": m["outcome"]
                },
                "similarity_score": m["similarity_score"],
                "mapped_ripple_explanation": "",
                "relevant_domains": []
            }
            for m in matches
        ]
        set_cached_analysis(article_id, cached)
        return cached["historical_matches"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"BigQuery vector retrieval collapsed: {str(e)}")

# 3. ADD NEW CONVERSATIONAL CHAT AGENT ENDPOINT (Track 1)
@app.post("/news/chat")
async def chat_about_report(req: Dict[str, Any]):
    article_id = req.get("article_id")
    user_message = req.get("message")
    history = req.get("history", [])  # List of dicts [{"role": "user"/"assistant", "content": "..."}]
    
    cached = get_cached_analysis(article_id)
    if not cached:
        raise HTTPException(status_code=404, detail="Analysis report must be loaded first.")
        
    # Serialize the entire dashboard output to act as the agent's real-time context
    context = f"""
    You are 'DE-INTEL Analyst', an elite, real-time strategic advisor. 
    You are helping an executive understand and drill down into a risk report.
    
    DASHBOARD INTELLIGENCE CONTEXT:
    Primary Event: {cached['article']['title']}
    Detailed Summary: {cached['detailed_summary']}
    
    SYSTEMIC RIPPLE EFFECTS:
    {json.dumps(cached['ripple_effects'], indent=2)}
    
    HISTORICAL ANALOGUES:
    {json.dumps(cached['historical_matches'], indent=2)}
    
    STRATEGIC RECOMMENDATIONS:
    {json.dumps(cached['recommendations'], indent=2)}
    
    Instructions:
    - Answer the user's questions strictly using the provided context.
    - If the user asks about something outside the context, utilize your intelligence background to reason through it, but prioritize linking back to the historical matches or ripple effects.
    - Keep responses concise, objective, and written in a professional, executive-ready tone.
    """
    
    from google.genai import types
    
    # Format chat history for Google Gen AI SDK
    contents = []
    for h in history:
        role = "user" if h["role"] == "user" else "model"
        contents.append(types.Content(role=role, parts=[types.Part.from_text(text=h["content"])]))

    # Include current user message
    contents.append(types.Content(role="user", parts=[types.Part.from_text(text=user_message)]))
    
    # Config with system instruction context
    config = types.GenerateContentConfig(system_instruction=context)
    
    try:
        response = await asyncio.to_thread(
            gemini_service.client.models.generate_content,
            model=gemini_service.model_id,
            contents=contents,
            config=config
        )
        return {"response": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent response failed: {str(e)}")

@app.post("/history/explain")
async def explain_history(req: Dict[str, Any]):
    article_id = req.get("article_id")
    cached = get_cached_analysis(article_id)
    if not cached:
        raise HTTPException(status_code=404, detail="Cache directory state not verified.")
        
    if cached.get("historical_matches") and cached["historical_matches"][0].get("mapped_ripple_explanation"):
        return cached["historical_matches"]
        
    hist_matches_raw = cached.get("historical_matches", [])
    if not hist_matches_raw:
        raise HTTPException(status_code=400, detail="No historical analogues found. Please ensure the BigQuery 'historical_events' table is populated with embedded data.")
        
    try:
        events_for_prompt = [hm["historical_event"] for hm in hist_matches_raw]
        explanations_data = await gemini_service.explain_historical_ripples(
            current_summary=cached["detailed_summary"],
            historical_events=events_for_prompt
        )
        
        explanations_list = explanations_data.get("explanations", [])
        for idx, hm in enumerate(hist_matches_raw):
            item = explanations_list[idx] if idx < len(explanations_list) else (explanations_list[0] if explanations_list else {})
            hm["mapped_ripple_explanation"] = item.get("mapped_ripple_explanation", "")
            hm["relevant_domains"] = item.get("relevant_domains", [])
                
        cached["historical_matches"] = hist_matches_raw
        set_cached_analysis(article_id, cached)
        return cached["historical_matches"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reasoning Core could not align historical precedents: {str(e)}")

@app.post("/recommendations/generate")
async def generate_recs(req: Dict[str, Any]):
    article_id = req.get("article_id")
    cached = get_cached_analysis(article_id)
    if not cached:
        raise HTTPException(status_code=404, detail="Cache directory state not verified.")
        
    if cached.get("recommendations"):
        return cached["recommendations"]
        
    try:
        ripples_objs = [RippleEffect(**r) for r in cached["ripple_effects"]]
        recs_data = await gemini_service.generate_recommendations(
            current_summary=cached["detailed_summary"],
            ripple_effects=ripples_objs,
            historical_explanations=cached["historical_matches"]
        )
        
        cached["recommendations"] = recs_data.get("recommendations", [])
        set_cached_analysis(article_id, cached)
        return cached["recommendations"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Strategic recommendation engine failed: {str(e)}")

@app.get("/briefing/visual")
async def get_visual_briefing_html(article_id: str, domain: str = "All"):
    data = get_cached_analysis(article_id)
    if not data:
        raise HTTPException(status_code=404, detail="Master cache directory missing complete dataset.")
        
    report = CompleteAnalysisReport(**data)
    
    ripples_by_domain = {}
    for r in report.ripple_effects:
        ripples_by_domain.setdefault(r.domain, []).append(r)
        
    top_hist = None
    if report.historical_matches:
        sorted_hist = sorted(report.historical_matches, key=lambda x: x.similarity_score, reverse=True)
        top_hist = sorted_hist[0]
        
    top_rec = None
    if report.recommendations:
        def parse_prob(r):
            try:
                return int(str(r.probability).replace('%', ''))
            except:
                return 0
        sorted_recs = sorted(report.recommendations, key=parse_prob, reverse=True)
        top_rec = sorted_recs[0]
        
    domains_list = []
    for d_name, d_ripples in ripples_by_domain.items():
        d_hist = next((h for h in report.historical_matches if d_name in h.relevant_domains), None)
        if not d_hist and report.historical_matches:
            d_hist = report.historical_matches[0]
            
        d_rec = next((rec for rec in report.recommendations if d_name in rec.relevant_domains), None)
        if not d_rec and report.recommendations:
            d_rec = report.recommendations[0]
            
        domains_list.append(DomainBriefing(
            domain=d_name,
            ripple_effects=d_ripples,
            top_historical_match=d_hist,
            top_recommendation=d_rec
        ))
        
    generic_top_ripples = []
    for d_name, d_ripples in ripples_by_domain.items():
        sorted_d_ripples = sorted(d_ripples, key=lambda x: x.impact_score, reverse=True)
        generic_top_ripples.append(sorted_d_ripples[0])
        
    briefing = VisualBriefing(
        article_id=article_id,
        domains=domains_list,
        generic_top_ripples=generic_top_ripples,
        top_historical_analogue=top_hist,
        top_recommendation=top_rec
    )
    
    from briefing import render_visual_briefing_html
    html_content = render_visual_briefing_html(briefing, domain)
    return {"html": html_content, "available_domains": list(ripples_by_domain.keys())}