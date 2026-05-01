import logging
from fastapi import APIRouter, HTTPException
from backend.database import run_query

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/analytics", tags=["analytics"])

@router.get("/top-titles")
async def top_titles():
    try:
        result = run_query("""
            SELECT m.title, m.genre, m.imdb_rating, m.revenue_usd,
                   COUNT(w.activity_id) as total_views,
                   ROUND(AVG(w.completion_pct),1) as avg_completion
            FROM movies m
            LEFT JOIN watch_activity w ON m.movie_id = w.movie_id
            GROUP BY m.movie_id
            ORDER BY total_views DESC
            LIMIT 10
        """)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/genre-performance")
async def genre_performance():
    try:
        result = run_query("""
            SELECT m.genre,
                   COUNT(DISTINCT m.movie_id) as title_count,
                   ROUND(AVG(m.imdb_rating),2) as avg_rating,
                   SUM(m.revenue_usd) as total_revenue,
                   ROUND(AVG(w.completion_pct),1) as avg_completion
            FROM movies m
            LEFT JOIN watch_activity w ON m.movie_id = w.movie_id
            GROUP BY m.genre
            ORDER BY total_revenue DESC
        """)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/city-engagement")
async def city_engagement():
    try:
        result = run_query("""
            SELECT city,
                   SUM(views) as total_views,
                   ROUND(AVG(avg_rating),2) as avg_rating,
                   ROUND(AVG(engagement_score),2) as avg_engagement,
                   SUM(revenue_usd) as total_revenue
            FROM regional_performance
            GROUP BY city
            ORDER BY total_views DESC
        """)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/platform-stats")
async def platform_stats():
    try:
        result = run_query("""
            SELECT platform,
                   COUNT(*) as sessions,
                   ROUND(AVG(completion_pct),1) as avg_completion,
                   ROUND(AVG(rating_given),2) as avg_rating
            FROM watch_activity
            GROUP BY platform
            ORDER BY sessions DESC
        """)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/marketing-roi")
async def marketing_roi():
    try:
        result = run_query("""
            SELECT channel,
                   SUM(spend_usd) as total_spend,
                   SUM(impressions) as total_impressions,
                   SUM(conversions) as total_conversions,
                   ROUND(CAST(SUM(conversions) AS FLOAT)/SUM(spend_usd)*1000,2) as conversions_per_1k_spend
            FROM marketing_spend
            GROUP BY channel
            ORDER BY conversions_per_1k_spend DESC
        """)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
