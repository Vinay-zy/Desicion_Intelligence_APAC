# backend/database.py
import os
import json
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from google.cloud import bigquery

# Resolve project ID from environment or client discovery
PROJECT_ID = os.getenv("GCP_PROJECT_ID") or os.getenv("GOOGLE_CLOUD_PROJECT")
bq_client = bigquery.Client(project=PROJECT_ID)
if not PROJECT_ID:
    PROJECT_ID = bq_client.project

DATASET_ID = "de_intel_dataset"
HEADLINE_TABLE = f"{PROJECT_ID}.{DATASET_ID}.headline_cache"
ANALYSIS_TABLE = f"{PROJECT_ID}.{DATASET_ID}.analysis_cache"

def init_db():
    # Ensure the master dataset exists
    dataset = bigquery.Dataset(f"{PROJECT_ID}.{DATASET_ID}")
    dataset.location = os.getenv("GCP_REGION", "us-central1")
    bq_client.create_dataset(dataset, exists_ok=True)
    
    # 1. Initialize Headline Cache Table
    schema_headline = [
        bigquery.SchemaField("date_key", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("category", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("data", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
    ]
    table_headline = bigquery.Table(HEADLINE_TABLE, schema=schema_headline)
    bq_client.create_table(table_headline, exists_ok=True)
    
    # 2. Initialize Analysis Report Cache Table
    schema_analysis = [
        bigquery.SchemaField("article_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("data", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
    ]
    table_analysis = bigquery.Table(ANALYSIS_TABLE, schema=schema_analysis)
    bq_client.create_table(table_analysis, exists_ok=True)

def get_cached_headlines(date_key: str, category: str) -> Optional[list]:
    if not isinstance(date_key, str):
        date_key = str(date_key)
    query = f"""
        SELECT data FROM `{HEADLINE_TABLE}`
        WHERE date_key = @date_key AND category = @category
        ORDER BY created_at DESC
        LIMIT 1
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("date_key", "STRING", date_key),
            bigquery.ScalarQueryParameter("category", "STRING", category)
        ]
    )
    try:
        query_job = bq_client.query(query, job_config=job_config)
        rows = list(query_job.result())
        if rows:
            return json.loads(rows[0]["data"])
    except Exception as e:
        print(f"Error reading headline cache from BigQuery: {e}")
    return None

def set_cached_headlines(date_key: str, category: str, headlines: list):
    if not isinstance(date_key, str):
        date_key = str(date_key)
    try:
        rows_to_insert = [{
            "date_key": date_key, 
            "category": category, 
            "data": json.dumps(headlines),
            "created_at": datetime.now(timezone.utc).isoformat()
        }]
        bq_client.insert_rows_json(HEADLINE_TABLE, rows_to_insert)
    except Exception as e:
        print(f"Error writing headline cache to BigQuery: {e}")

def get_cached_analysis(article_id: str) -> Optional[Dict[str, Any]]:
    query = f"""
        SELECT data FROM `{ANALYSIS_TABLE}`
        WHERE article_id = @article_id
        ORDER BY created_at DESC
        LIMIT 1
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("article_id", "STRING", article_id)
        ]
    )
    try:
        query_job = bq_client.query(query, job_config=job_config)
        rows = list(query_job.result())
        if rows:
            return json.loads(rows[0]["data"])
    except Exception as e:
        print(f"Error reading analysis cache from BigQuery: {e}")
    return None

def set_cached_analysis(article_id: str, analysis_data: Dict[str, Any]):
    try:
        rows_to_insert = [{
            "article_id": article_id, 
            "data": json.dumps(analysis_data),
            "created_at": datetime.now(timezone.utc).isoformat()
        }]
        bq_client.insert_rows_json(ANALYSIS_TABLE, rows_to_insert)
    except Exception as e:
        print(f"Error writing analysis cache to BigQuery: {e}")