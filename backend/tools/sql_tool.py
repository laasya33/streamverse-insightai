import logging
from backend.database import run_query, get_schema

logger = logging.getLogger(__name__)

TOOL_DEFINITION = {
    "name": "query_sql_database",
    "description": (
        "Query the StreamVerse SQLite database containing structured business data. "
        "Tables: movies (title,genre,release_year,imdb_rating,budget_usd,revenue_usd), "
        "viewers (viewer_id,age_group,gender,city,subscription_plan,is_active), "
        "watch_activity (viewer_id,movie_id,watch_date,watch_duration_min,completion_pct,platform,rating_given), "
        "reviews (movie_id,viewer_id,sentiment,score,review_text,review_date), "
        "marketing_spend (movie_id,channel,month,year,spend_usd,impressions,clicks,conversions), "
        "regional_performance (movie_id,city,month,year,views,avg_rating,engagement_score,revenue_usd). "
        "Use SQL SELECT queries only. Always use table aliases. Limit results to 50 rows max."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "sql": {
                "type": "string",
                "description": "A valid SQLite SELECT query. No INSERT/UPDATE/DELETE allowed."
            }
        },
        "required": ["sql"]
    }
}

def execute(sql: str) -> dict:
    sql = sql.strip()
    forbidden = ["insert", "update", "delete", "drop", "alter", "create"]
    if any(kw in sql.lower() for kw in forbidden):
        return {"error": "Only SELECT queries are permitted.", "source": "Internal data and business reports"}
    logger.info(f"SQL query: {sql}")
    result = run_query(sql)
    result["source"] = "Internal data and business reports"
    result["query"] = sql
    return result
