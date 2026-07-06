# backend/bigquery_service.py
import os
from typing import List, Dict, Any
from google.cloud import bigquery

class BigQueryService:
    def __init__(self):
        # Use consistent project resolution across services
        self.project_id = os.getenv("GCP_PROJECT_ID") or os.getenv("GOOGLE_CLOUD_PROJECT")
        self.client = bigquery.Client(project=self.project_id)
        if not self.project_id:
            self.project_id = self.client.project
        self.dataset_table = f"{self.project_id}.de_intel_dataset.historical_events"

    def query_similar_events(self, query_embedding: List[float], n_results: int = 4) -> List[Dict[str, Any]]:
        # Compute Cosine Similarity using ML.DISTANCE on BigQuery[<vertex-ai-rich-citation-chip>3</vertex-ai-rich-citation-chip>]
        sql_query = f"""
            SELECT id, title, date, description, sector, outcome,
                   (1.0 - ML.DISTANCE(embedding, @query_embedding, 'COSINE')) AS similarity_score
            FROM `{self.dataset_table}`
            ORDER BY similarity_score DESC
            LIMIT @top_k
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ArrayQueryParameter("query_embedding", "FLOAT64", query_embedding),
                bigquery.ScalarQueryParameter("top_k", "INT64", n_results),
            ]
        )
        
        query_job = self.client.query(sql_query, job_config=job_config)
        results = query_job.result()
        
        matches = []
        for row in results:
            matches.append({
                "id": row["id"],
                "title": row["title"],
                "date": row["date"],
                "description": row["description"],
                "sector": row["sector"],
                "outcome": row["outcome"],
                "similarity_score": round(float(row["similarity_score"]), 3)
            })
        return matches