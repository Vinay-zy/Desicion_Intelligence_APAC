from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class Article(BaseModel):
    id: str
    title: str
    source: str
    category: str
    url: str
    published_at: str
    content: Optional[str] = None
    entities: List[str] = Field(default_factory=list)
    short_summary: Optional[str] = None

class RippleEffect(BaseModel):
    domain: str  # Market/Financial, Regulatory/Policy, Geopolitical, Social/Public Sentiment, Competitive/Industry, Supply Chain, Technology
    direction: str  # positive, negative, mixed
    time_horizon: str  # short, medium, long
    confidence: str  # high, medium, low
    description: str
    impact_score: int = Field(..., ge=1, le=5)

class HistoricalEvent(BaseModel):
    id: str
    title: str
    date: str
    description: str
    sector: str
    outcome: str

class HistoricalMatch(BaseModel):
    historical_event: HistoricalEvent
    similarity_score: float
    mapped_ripple_explanation: str
    relevant_domains: List[str]

class Recommendation(BaseModel):
    text: str
    probability: str  # e.g., "75%"
    best_case: str
    base_case: str
    worst_case: str
    supporting_analogue: str
    relevant_domains: List[str]

class DomainBriefing(BaseModel):
    domain: str
    ripple_effects: List[RippleEffect]
    top_historical_match: Optional[HistoricalMatch] = None
    top_recommendation: Optional[Recommendation] = None

class VisualBriefing(BaseModel):
    article_id: str
    domains: List[DomainBriefing]
    generic_top_ripples: List[RippleEffect]
    top_historical_analogue: Optional[HistoricalMatch] = None
    top_recommendation: Optional[Recommendation] = None

class CompleteAnalysisReport(BaseModel):
    article: Article
    entities: List[str]
    event_type: str
    detailed_summary: str
    connected_events: List[Dict[str, Any]]
    ripple_effects: List[RippleEffect]
    historical_matches: List[HistoricalMatch]
    recommendations: List[Recommendation]