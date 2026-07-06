import os
import json
import asyncio
from google import genai
from google.genai import types

class GeminiService:
    def __init__(self):
        api_key = os.environ.get("GEMINI_API_KEY")
        project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
        location = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")

        # Fallback for Project ID discovery in Cloud Shell
        if not project_id:
            try:
                import google.auth
                _, project_id = google.auth.default()
            except Exception:
                project_id = None

        # Initialize the new Google Gen AI SDK Client for Vertex AI
        self.client = genai.Client(
            vertexai=True,
            project=project_id,
            location=location
        )
        
        self.model_id = "gemini-2.5-flash"
        self.embedding_model_id = "text-embedding-005"
        
        # Build Google Search Tool using new SDK types
        self.google_search_tool = types.Tool(
            google_search=types.GoogleSearch()
        )

    async def get_embedding(self, text: str) -> list:
        try:
            res = await asyncio.to_thread(
                self.client.models.embed_content,
                model=self.embedding_model_id,
                contents=text
            )
            return res.embeddings[0].values
        except Exception as e:
            print(f"Critical Embedding failure: {e}")
            raise e

    async def call_gemini_json(self, prompt: str, use_search: bool = False) -> dict:
        # Controlled generation (response_mime_type="application/json") is currently 
        # not supported when using grounding tools like Google Search on Vertex AI.
        if use_search:
            config = types.GenerateContentConfig(
                temperature=0.15,
                tools=[self.google_search_tool]
            )
        else:
            config = types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.15
            )
        
        # Safe retry mechanism
        for attempt in range(2):
            try:
                response = await asyncio.to_thread(
                    self.client.models.generate_content,
                    model=self.model_id,
                    contents=prompt,
                    config=config
                )
                text = response.text.strip()
                if text.startswith("```json"):
                    text = text[7:]
                if text.endswith("```"):
                    text = text[:-3]
                return json.loads(text.strip())
            except Exception as e:
                print(f"Vertex AI Gemini Call failure (attempt {attempt+1}): {e}")
                if attempt == 1:
                    raise e
        return {}

    async def fetch_todays_headlines(self, category: str, current_date: str) -> list:
        prompt = f"""
        Search for major news stories and prominent headlines from today (date: {current_date}) in the category '{category}'. 
        If no major news is found for that exact date, return the most recent significant news stories available.
        Find up to 8 real headlines. Never fabricate or hallucinate any news. 
        Only return real news items with proper news sources and valid URLs.
        
        You must return a JSON object with this exact structure:
        {{
          "headlines": [
            {{
              "id": "slug-like-unique-id-{category}-1",
              "title": "Exact clean headline",
              "source": "Name of source outlet (e.g. Reuters, TechCrunch)",
              "category": "{category}",
              "url": "Valid grounded source URL of the article",
              "published_at": "{current_date}",
              "short_summary": "1-2 sentence description explaining the key event"
            }}
          ]
        }}
        """
        res = await self.call_gemini_json(prompt, True)
        headlines = res.get("headlines", [])
        
        # Filter out incomplete headlines to prevent Pydantic validation 500 errors
        required_fields = {"id", "title", "source", "category", "url", "published_at"}
        return [h for h in headlines if all(field in h for field in required_fields)]

    async def deep_scan(self, title: str, url: str) -> dict:
        prompt = f"""
        You are a highly sophisticated Intelligence Analyst. 
        Analyze the following current news story:
        Title: {title}
        URL: {url}
        
        Using Google Search grounding, pull deeper context and related details about this specific story.
        Identify:
        1. Key entities (specifically people, organizations, countries, and sectors involved). Limit to the top 6.
        2. Core event type (e.g., 'Regulatory Crackdown', 'Geopolitical Conflict', 'Market Collapse', 'Supply Chain Blockade', etc.).
        3. A highly professional, detailed 2-paragraph executive summary of the event based on real search results.
        
        Return a JSON object matching this schema:
        {{
          "entities": ["entity1", "entity2", "entity3", ...],
          "event_type": "Core Event Type",
          "detailed_summary": "Detailed 2-paragraph analytical executive summary of the story, current status, and consequences."
        }}
        """
        return await self.call_gemini_json(prompt, True)

    async def discover_connected_events(self, title: str, entities: list, event_type: str, current_date: str) -> dict:
        entities_str = ", ".join(entities)
        prompt = f"""
        Search the web for today's ({current_date}) related or connected stories, events, or cascading reactions related to:
        Headline: "{title}"
        Key Entities: {entities_str}
        Event Type: {event_type}
        
        Find up to 4 other real, distinct news events occurring today or in the last 24 hours that are connected to this event.
        For each connected event, provide a clean rationale explaining how it connects to the primary event.
        Never fabricate headlines or URLs. Provide authentic source URLs.
        
        Return a JSON object with this exact schema:
        {{
          "connected_events": [
            {{
              "title": "Title of the connected news event",
              "source": "News outlet name",
              "url": "Authentic source URL of this connected story",
              "published_at": "{current_date}",
              "rationale": "One-sentence analytical explanation of why this story is connected to the primary event."
            }}
          ]
        }}
        """
        return await self.call_gemini_json(prompt, True)

    async def predict_ripple_effects(self, title: str, summary: str, connected_events: list) -> dict:
        conn_str = "\n".join([f"- {e['title']} (Source: {e['source']})" for e in connected_events])
        prompt = f"""
        Analyze the following primary news event and its related developments:
        Primary Event: {title}
        Summary: {summary}
        
        Related Developments today:
        {conn_str}
        
        Project the second- and third-order ripple effects across the following domains simultaneously:
        - Market/Financial
        - Regulatory/Policy
        - Geopolitical
        - Social/Public Sentiment
        - Competitive/Industry
        - Supply Chain
        - Technology
        
        Do not force-fit every domain, but actively scan across all of them. Only return domains where a genuine, logical ripple effect is predicted.
        Return 4 to 6 distinct ripple effects.
        
        Return a JSON object matching this schema:
        {{
          "ripple_effects": [
            {{
              "domain": "One of: Market/Financial, Regulatory/Policy, Geopolitical, Social/Public Sentiment, Competitive/Industry, Supply Chain, Technology",
              "direction": "positive | negative | mixed",
              "time_horizon": "short | medium | long",
              "confidence": "high | medium | low",
              "description": "Clear 1-2 sentence forecast of what will happen in this domain and why.",
              "impact_score": 4  // Integer from 1 (minimal impact) to 5 (extreme systemic impact)
            }}
          ]
        }}
        """
        return await self.call_gemini_json(prompt, False)

    async def explain_historical_ripples(self, current_summary: str, historical_events: list) -> dict:
        hist_serialized = ""
        for idx, h in enumerate(historical_events):
            hist_serialized += f"--- ANALOGUE #{idx+1} ---\nTitle: {h['title']}\nDate: {h['date']}\nDescription: {h['description']}\nSector: {h['sector']}\nOutcome: {h['outcome']}\n\n"
            
        prompt = f"""
        Compare this current event:
        "{current_summary}"
        
        With these historical analogues:
        {hist_serialized}
        
        For each historical analogue, analyze:
        1. What actually happened and what ripple effects followed historically.
        2. How closely the historical pattern maps to the current situation (a detailed similarity rationale).
        3. Which domains (Market/Financial, Regulatory/Policy, Geopolitical, Social/Public Sentiment, Competitive/Industry, Supply Chain, Technology) are most relevant to this comparison.
        
        Return a JSON object containing a list of explanations. The ordering must match the analogues provided above.
        Schema:
        {{
          "explanations": [
            {{
              "title": "Title of historical analogue",
              "mapped_ripple_explanation": "Detailed explanation (3-4 sentences) of what happened historically and how it relates directly to the current scenario's trajectory.",
              "relevant_domains": ["domain1", "domain2", ...] // List of domains that overlap strongly between the historical and current event
            }}
          ]
        }}
        """
        return await self.call_gemini_json(prompt, False)

    async def generate_recommendations(self, current_summary: str, ripple_effects: list, historical_explanations: list) -> dict:
        ripples_str = "\n".join([f"- [{r.domain}] {r.description} (Impact: {r.impact_score})" for r in ripple_effects])
        hist_str = "\n".join([f"- {h['historical_event']['title']}: {h['mapped_ripple_explanation']}" for h in historical_explanations])
        
        prompt = f"""
        You are a highly strategic Executive Advisor. 
        Synthesize the following intelligence dashboard data:
        
        CURRENT EVENT SUMMARY:
        {current_summary}
        
        PREDICTED RIPPLE EFFECTS:
        {ripples_str}
        
        HISTORICAL ANALOGUES & LESSONS:
        {hist_str}
        
        Generate 3 to 5 probabilistic executive recommendations. Each recommendation must be action-oriented, clear, and highly specific to navigating the risk or opportunity surfaced above.
        
        Return a JSON object with this exact schema:
        {{
          "recommendations": [
            {{
              "text": "Action-oriented recommendation (e.g., 'Diversify tier-1 supplier nodes...')",
              "probability": "percentage likelihood of success or scenario materialization (e.g., '75%')",
              "best_case": "Forecast of the best-case outcome if this recommendation is followed.",
              "base_case": "Forecast of the base-case/most likely outcome if followed.",
              "worst_case": "Forecast of the worst-case scenario if ignored or implemented poorly.",
              "supporting_analogue": "Briefly name the historical analogue that supports or validates this strategy.",
              "relevant_domains": ["domain1", "domain2", ...] // Which domains this recommendation is designed to mitigate or capitalize on
            }}
          ]
        }}
        """
        return await self.call_gemini_json(prompt, False)