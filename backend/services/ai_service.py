import os
import json
import logging
import re

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────
# TASK 2 — Change model by editing ONE line only
# ──────────────────────────────────────────────
GROQ_MODEL = "llama-3.1-8b-instant"   # ← swap to this for faster, cheaper responses (good for testing)
# GROQ_MODEL = "mixtral-8x7b-32768"   ← swap to this anytime


def _get_groq_client():
    """Return an OpenAI-compatible Groq client."""
    try:
        from openai import OpenAI
    except ImportError:
        raise RuntimeError(
            "openai package not installed. Run: pip install openai"
        )
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not set in environment")
    return OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")


# ──────────────────────────────────────────────
# DB helpers
# ──────────────────────────────────────────────
def _query_db(sql: str) -> list:
    try:
        from backend.database import run_query
        res = run_query(sql)
        return res.get("rows", [])
    except Exception as e:
        logger.error(f"DB query error: {e}")
        return []


def _get_schema() -> dict:
    try:
        from backend.database import get_schema
        return get_schema()
    except Exception as e:
        logger.error(f"Schema fetch error: {e}")
        return {}


# ──────────────────────────────────────────────
# PDF helper
# ──────────────────────────────────────────────
def _get_pdf(query: str) -> str:
    try:
        from backend.tools.pdf_tool import execute as pdf_execute
        result = pdf_execute(document="all", query=query)
        docs = result.get("results", {})
        if not docs or "info" in docs:
            return ""
        lines = []
        for doc_name, doc_lines in docs.items():
            for line in doc_lines[:5]:
                lines.append(f"[{doc_name}] {line}")
        return "\n".join(lines[:20])
    except Exception as e:
        logger.error(f"PDF fetch error: {e}")
        return ""
# ──────────────────────────────────────────────
# CSV helper
# ──────────────────────────────────────────────

def _get_csv(file: str, operation: str, params: dict = None) -> str:
    try:
        from backend.tools.csv_tool import execute as csv_execute

        result = csv_execute(file=file, operation=operation, params=params or {})

        rows = result.get("rows", [])
        if not rows:
            return ""

        return json.dumps(rows[:10], indent=2)

    except Exception as e:
        logger.error(f"CSV fetch error: {e}")
        return ""

# ──────────────────────────────────────────────
# TASK 1 — Robust multi-source context builder
# ──────────────────────────────────────────────
def _build_context(question: str) -> tuple[str, list]:
    """
    Pull data from SQL + PDF for EVERY question.
    Uses broad keyword matching so no question falls through.
    Always combines structured + unstructured sources.
    """
    q = question.lower()
    parts = []
    sources = []

    # ── 1. Top-performing titles ──────────────────────────────────────────
    if any(w in q for w in ["best", "top", "perform", "highest", "titles", "2025", "rank"]):
        rows = _query_db("""
            SELECT m.title, m.genre, m.language, m.imdb_rating,
                   COUNT(wa.activity_id)           AS total_views,
                   ROUND(AVG(wa.completion_pct),1) AS avg_completion_pct,
                   ROUND(AVG(wa.rating_given),1)   AS avg_viewer_rating,
                   m.revenue_usd
            FROM movies m
            LEFT JOIN watch_activity wa ON m.movie_id = wa.movie_id
            WHERE wa.watch_date LIKE '2025%'
            GROUP BY m.movie_id
            ORDER BY total_views DESC
            LIMIT 10
        """)
        if rows:
            parts.append("=== TOP TITLES (2025 watch data) ===\n" + json.dumps(rows, indent=2))
            sources.append("Sources: Internal data and business reports")
        pdf = _get_pdf("top performing titles revenue 2025 best")
        if pdf:
            parts.append("=== EXECUTIVE REPORT EXCERPTS ===\n" + pdf)
            sources.append("Sources: Internal data and business reports")
        csv = _get_csv(
        file="movies",
        operation="top_n",
        params={"column": "revenue_usd", "n": 10}
       )
        if csv:
            parts.append("=== CSV BUSINESS DATA ===\n" + csv)
            sources.append("Sources: Internal data and business reports")

    # ── 2. Stellar Run / trending ─────────────────────────────────────────
    if any(w in q for w in ["stellar", "trending", "viral", "spike"]):
        monthly = _query_db("""
            SELECT strftime('%Y-%m', wa.watch_date) AS month,
                   COUNT(*)                          AS views
            FROM watch_activity wa
            JOIN movies m ON wa.movie_id = m.movie_id
            WHERE m.title = 'Stellar Run'
            GROUP BY month ORDER BY month
        """)
        mkt = _query_db("""
            SELECT ms.channel,
                   SUM(ms.spend_usd)     AS total_spend,
                   SUM(ms.impressions)   AS total_impressions,
                   SUM(ms.clicks)        AS total_clicks,
                   SUM(ms.conversions)   AS total_conversions
            FROM marketing_spend ms
            JOIN movies m ON ms.movie_id = m.movie_id
            WHERE m.title = 'Stellar Run'
            GROUP BY ms.channel ORDER BY total_spend DESC
        """)
        reviews = _query_db("""
            SELECT r.sentiment,
                   COUNT(*)             AS count,
                   ROUND(AVG(r.score),1) AS avg_score
            FROM reviews r
            JOIN movies m ON r.movie_id = m.movie_id
            WHERE m.title = 'Stellar Run'
            GROUP BY r.sentiment
        """)
        if monthly:
            parts.append("=== STELLAR RUN — MONTHLY VIEWS ===\n" + json.dumps(monthly, indent=2))
            sources.append("Sources: Internal data and business reports")
        if mkt:
            parts.append("=== STELLAR RUN — MARKETING SPEND BY CHANNEL ===\n" + json.dumps(mkt, indent=2))
        if reviews:
            parts.append("=== STELLAR RUN — REVIEW SENTIMENT ===\n" + json.dumps(reviews, indent=2))
        pdf = _get_pdf("Stellar Run trending influencer campaign viral")
        if pdf:
            parts.append("=== CAMPAIGN REPORT EXCERPTS ===\n" + pdf)
            sources.append("Sources: Internal data and business reports")
        csv = _get_csv(
    file="watch_activity",
    operation="groupby",
    params={
        "by": "watch_date",
        "agg_column": "completion_pct",
        "agg_func": "mean"
    }
)
        if csv:
            parts.append("=== CSV INSIGHTS ===\n" + csv)
            sources.append("Sources: Internal data and business reports")

    # ── 3. Title comparison ───────────────────────────────────────────────
    if any(w in q for w in ["compare", "vs", "versus", "difference", "between"]):
        # Extract any quoted or recognisable titles; fall back to known pair
        known_titles = _query_db("SELECT DISTINCT title FROM movies")
        title_list = [r["title"] for r in known_titles] if known_titles else []
        matched = [t for t in title_list if t.lower() in q]
        if not matched:
            matched = ["Dark Orbit", "Last Kingdom"]   # default demo pair
        placeholders = ",".join(f"'{t}'" for t in matched)
        perf = _query_db(f"""
            SELECT m.title, m.genre, m.imdb_rating, m.budget_usd, m.revenue_usd,
                   COUNT(wa.activity_id)           AS views,
                   ROUND(AVG(wa.completion_pct),1) AS avg_completion,
                   ROUND(AVG(wa.rating_given),1)   AS avg_rating
            FROM movies m
            LEFT JOIN watch_activity wa ON m.movie_id = wa.movie_id
            WHERE m.title IN ({placeholders})
            GROUP BY m.movie_id
        """)
        revs = _query_db(f"""
            SELECT m.title,
                   SUM(CASE WHEN r.sentiment='positive' THEN 1 ELSE 0 END) AS positive,
                   SUM(CASE WHEN r.sentiment='negative' THEN 1 ELSE 0 END) AS negative,
                   ROUND(AVG(r.score),1)                                    AS avg_score
            FROM reviews r
            JOIN movies m ON r.movie_id = m.movie_id
            WHERE m.title IN ({placeholders})
            GROUP BY m.movie_id
        """)
        mkt = _query_db(f"""
            SELECT m.title, ms.channel,
                   SUM(ms.spend_usd)   AS spend,
                   SUM(ms.conversions) AS conversions
            FROM marketing_spend ms
            JOIN movies m ON ms.movie_id = m.movie_id
            WHERE m.title IN ({placeholders})
            GROUP BY m.movie_id, ms.channel
        """)
        if perf:
            parts.append(f"=== TITLE COMPARISON: {', '.join(matched)} — PERFORMANCE ===\n" + json.dumps(perf, indent=2))
            sources.append("Sources: Internal data and business reports")
        if revs:
            parts.append(f"=== TITLE COMPARISON: {', '.join(matched)} — REVIEWS ===\n" + json.dumps(revs, indent=2))
        if mkt:
            parts.append(f"=== TITLE COMPARISON: {', '.join(matched)} — MARKETING ===\n" + json.dumps(mkt, indent=2))

    # ── 4. City / regional engagement ─────────────────────────────────────
    if any(w in q for w in ["city", "cities", "region", "regional", "engagement",
                             "mumbai", "bangalore", "hyderabad", "delhi", "pune",
                             "strongest", "geography", "location"]):
        city_rows = _query_db("""
            SELECT rp.city,
                   SUM(rp.views)                    AS total_views,
                   ROUND(AVG(rp.engagement_score),3) AS avg_engagement,
                   ROUND(AVG(rp.avg_rating),2)       AS avg_rating,
                   SUM(rp.revenue_usd)               AS total_revenue,
                   rp.year, rp.month
            FROM regional_performance rp
            WHERE rp.year = (SELECT MAX(year) FROM regional_performance)
              AND rp.month = (
                  SELECT MAX(month) FROM regional_performance
                  WHERE year = (SELECT MAX(year) FROM regional_performance)
              )
            GROUP BY rp.city
            ORDER BY avg_engagement DESC
            LIMIT 15
        """)
        subscriber_city = _query_db("""
            SELECT v.city,
                   COUNT(*)                                              AS total_viewers,
                   SUM(CASE WHEN v.subscription_plan='Premium' THEN 1 ELSE 0 END) AS premium_count,
                   SUM(CASE WHEN v.is_active='Yes' THEN 1 ELSE 0 END)  AS active_viewers
            FROM viewers v
            GROUP BY v.city ORDER BY total_viewers DESC LIMIT 10
        """)
        if city_rows:
            parts.append("=== CITY ENGAGEMENT (latest month) ===\n" + json.dumps(city_rows, indent=2))
            sources.append("Sources: Internal data and business reports")
        if subscriber_city:
            parts.append("=== SUBSCRIBER COUNT BY CITY ===\n" + json.dumps(subscriber_city, indent=2))
        pdf = _get_pdf("city engagement Mumbai Bangalore Hyderabad regional audience")
        if pdf:
            parts.append("=== AUDIENCE REPORT EXCERPTS ===\n" + pdf)
            sources.append("Sources: Internal data and business reports")
        csv = _get_csv(
            file="regional_performance",
            operation="groupby",
            params={"by": "city", "agg_column": "revenue_usd", "agg_func": "sum"}
        )
        if csv:
            parts.append("=== CSV CITY DATA ===\n" + csv)
            sources.append("Sources: Internal data and business reports")
    

    # ── 5. Comedy / weak genre ────────────────────────────────────────────
    if any(w in q for w in ["comedy", "weak", "poor", "underperform", "low rating",
                             "bad", "worst", "fail", "explain", "why"]):
        genre_breakdown = _query_db("""
            SELECT m.genre,
                   COUNT(DISTINCT m.movie_id)        AS title_count,
                   COUNT(wa.activity_id)              AS total_views,
                   ROUND(AVG(wa.completion_pct),1)   AS avg_completion_pct,
                   ROUND(AVG(wa.rating_given),1)     AS avg_viewer_rating,
                   ROUND(AVG(m.imdb_rating),2)       AS avg_imdb_rating,
                   SUM(m.revenue_usd)                AS total_revenue
            FROM movies m
            LEFT JOIN watch_activity wa ON m.movie_id = wa.movie_id
            GROUP BY m.genre ORDER BY avg_completion_pct ASC
        """)
        comedy_reviews = _query_db("""
            SELECT r.sentiment,
                   COUNT(*)              AS count,
                   ROUND(AVG(r.score),1) AS avg_score,
                   GROUP_CONCAT(SUBSTR(r.review_text,1,80), ' | ') AS sample_reviews
            FROM reviews r
            JOIN movies m ON r.movie_id = m.movie_id
            WHERE m.genre = 'Comedy'
            GROUP BY r.sentiment
        """)
        comedy_mkt = _query_db("""
            SELECT ms.channel,
                   SUM(ms.spend_usd)   AS spend,
                   SUM(ms.conversions) AS conversions,
                   ROUND(CAST(SUM(ms.conversions) AS FLOAT)/NULLIF(SUM(ms.spend_usd),0)*1000,2) AS conv_per_1k
            FROM marketing_spend ms
            JOIN movies m ON ms.movie_id = m.movie_id
            WHERE m.genre = 'Comedy'
            GROUP BY ms.channel ORDER BY spend DESC
        """)
        if genre_breakdown:
            parts.append("=== GENRE PERFORMANCE BREAKDOWN ===\n" + json.dumps(genre_breakdown, indent=2))
            sources.append("Sources: Internal data and business reports")
        if comedy_reviews:
            parts.append("=== COMEDY REVIEW SENTIMENT ===\n" + json.dumps(comedy_reviews, indent=2))
        if comedy_mkt:
            parts.append("=== COMEDY MARKETING SPEND vs CONVERSIONS ===\n" + json.dumps(comedy_mkt, indent=2))
        pdf = _get_pdf("comedy weak underperform completion writing quality poor")
        if pdf:
            parts.append("=== REPORT EXCERPTS (Comedy Analysis) ===\n" + pdf)
            sources.append("Sources: Internal data and business reports")

    # ── 6. Strategy / leadership / recommendations ────────────────────────
    if any(w in q for w in ["recommend", "strategy", "leadership", "next quarter",
                             "action", "invest", "plan", "roadmap", "should"]):
        genre_roi = _query_db("""
            SELECT m.genre,
                   COUNT(DISTINCT m.movie_id)       AS titles,
                   ROUND(AVG(wa.completion_pct),1)  AS avg_completion,
                   SUM(m.revenue_usd)               AS total_revenue,
                   SUM(ms.spend_usd)                AS total_marketing_spend,
                   ROUND(SUM(m.revenue_usd)/NULLIF(SUM(ms.spend_usd),0),2) AS revenue_per_spend
            FROM movies m
            LEFT JOIN watch_activity wa ON m.movie_id = wa.movie_id
            LEFT JOIN marketing_spend ms ON m.movie_id = ms.movie_id
            GROUP BY m.genre ORDER BY revenue_per_spend DESC
        """)
        top_cities = _query_db("""
            SELECT rp.city,
                   SUM(rp.views)          AS total_views,
                   SUM(rp.revenue_usd)    AS total_revenue,
                   ROUND(AVG(rp.engagement_score),3) AS avg_engagement
            FROM regional_performance rp
            GROUP BY rp.city ORDER BY total_revenue DESC LIMIT 8
        """)
        platform_perf = _query_db("""
            SELECT wa.platform,
                   COUNT(*)                      AS sessions,
                   ROUND(AVG(wa.completion_pct),1) AS avg_completion
            FROM watch_activity wa
            GROUP BY wa.platform ORDER BY sessions DESC
        """)
        age_seg = _query_db("""
            SELECT v.age_group,
                   COUNT(*)                                               AS viewers,
                   SUM(CASE WHEN v.subscription_plan='Premium' THEN 1 ELSE 0 END) AS premium,
                   ROUND(AVG(wa.completion_pct),1)                       AS avg_completion
            FROM viewers v
            JOIN watch_activity wa ON v.viewer_id = wa.viewer_id
            GROUP BY v.age_group ORDER BY avg_completion DESC
        """)
        if genre_roi:
            parts.append("=== GENRE ROI ===\n" + json.dumps(genre_roi, indent=2))
            sources.append("Sources: Internal data and business reports")
        if top_cities:
            parts.append("=== TOP CITIES BY REVENUE ===\n" + json.dumps(top_cities, indent=2))
        if platform_perf:
            parts.append("=== PLATFORM PERFORMANCE ===\n" + json.dumps(platform_perf, indent=2))
        if age_seg:
            parts.append("=== AUDIENCE SEGMENT COMPLETION RATES ===\n" + json.dumps(age_seg, indent=2))
        pdf = _get_pdf("recommendation leadership strategy invest sci-fi comedy roadmap Q2")
        if pdf:
            parts.append("=== STRATEGY REPORT EXCERPTS ===\n" + pdf)
            sources.append("Sources: Internal data and business reports")

    # ── 7. Marketing / ROI / channel ─────────────────────────────────────
    if any(w in q for w in ["marketing", "campaign", "roi", "channel", "spend",
                             "influencer", "youtube", "social", "tv ad"]):
        mkt_summary = _query_db("""
            SELECT ms.channel,
                   SUM(ms.spend_usd)   AS total_spend,
                   SUM(ms.impressions) AS total_impressions,
                   SUM(ms.clicks)      AS total_clicks,
                   SUM(ms.conversions) AS total_conversions,
                   ROUND(CAST(SUM(ms.conversions) AS FLOAT)/NULLIF(SUM(ms.spend_usd),0)*1000,2) AS conv_per_1k_spend
            FROM marketing_spend ms
            GROUP BY ms.channel ORDER BY conv_per_1k_spend DESC
        """)
        if mkt_summary:
            summary = [
    f"{r['channel']} | spend: {r['total_spend']} | conversions: {r['total_conversions']} | conv/1k: {r['conv_per_1k_spend']}"
    for r in mkt_summary[:5]
]

        parts.append("=== MARKETING CHANNEL PERFORMANCE ===\n" + "\n".join(summary))
        sources.append("Sources: Internal data and business reports")
        pdf = _get_pdf("marketing ROI campaign channel influencer YouTube social")
        if pdf:
            parts.append("=== CAMPAIGN REPORT EXCERPTS ===\n" + pdf)
            sources.append("Sources: Internal data and business reports")

    # ── 8. Audience / viewer segments ─────────────────────────────────────
    if any(w in q for w in ["audience", "viewer", "segment", "age", "premium",
                             "subscriber", "retention", "churn", "25-34", "platform"]):
        seg = _query_db("""
            SELECT v.age_group, v.subscription_plan,
                   COUNT(*)                       AS viewer_count,
                   ROUND(AVG(wa.completion_pct),1) AS avg_completion,
                   ROUND(AVG(wa.rating_given),1)  AS avg_rating
            FROM viewers v
            JOIN watch_activity wa ON v.viewer_id = wa.viewer_id
            GROUP BY v.age_group, v.subscription_plan
            ORDER BY avg_completion DESC
        """)
        platform_seg = _query_db("""
            SELECT wa.platform, COUNT(*) AS sessions,
                   ROUND(AVG(wa.completion_pct),1) AS avg_completion
            FROM watch_activity wa
            GROUP BY wa.platform ORDER BY sessions DESC
        """)
        if seg:
            parts.append("=== AUDIENCE SEGMENT METRICS ===\n" + json.dumps(seg, indent=2))
            sources.append("Sources: Internal data and business reports")
        if platform_seg:
            parts.append("=== PLATFORM USAGE ===\n" + json.dumps(platform_seg, indent=2))
        pdf = _get_pdf("audience behavior age segment premium churn mobile platform")
        if pdf:
            parts.append("=== AUDIENCE BEHAVIOR REPORT EXCERPTS ===\n" + pdf)
            sources.append("Sources: Internal data and business reports")

    # ── 9. Fallback — always return overview if nothing matched ───────────
    if not parts:
        overview = _query_db("""
            SELECT m.title, m.genre, m.imdb_rating,
                   COUNT(wa.activity_id)           AS views,
                   ROUND(AVG(wa.completion_pct),1) AS avg_completion,
                   ROUND(AVG(wa.rating_given),1)   AS avg_rating,
                   m.revenue_usd
            FROM movies m
            LEFT JOIN watch_activity wa ON m.movie_id = wa.movie_id
            GROUP BY m.movie_id ORDER BY views DESC LIMIT 15
        """)
        if overview:
            parts.append("=== CONTENT OVERVIEW ===\n" + json.dumps(overview, indent=2))
            sources.append("Sources: Internal data and business reports")
        pdf = _get_pdf(question[:120])
        if pdf:
            parts.append("=== RELEVANT REPORT EXCERPTS ===\n" + pdf)
            sources.append("Sources: Internal data and business reports")
        # 🔥 FORCE CSV inclusion if nothing used yet
        if "CSV" not in "".join(parts):
            csv = _get_csv(question)
        if csv:
            parts.append("=== ADDITIONAL CSV DATA ===\n" + csv)
            sources.append("Sources:Internal data")

    return "\n\n".join(parts), list(set(sources))


# ──────────────────────────────────────────────
# TASK 3 — Strict system prompt: data-only answers
# ──────────────────────────────────────────────
SYSTEM_PROMPT = """You are InsightAI, an internal analytics assistant for StreamVerse Entertainment.

STRICT RULES — follow every rule without exception:
1. Answer ONLY using the DATA provided below. Do not use any outside knowledge.
2. If the data does not contain enough information to answer, say exactly:
   "I don't have enough data to answer this question."
3. Be concise and direct. No greetings, no filler, no disclaimers, no generic advice.
4. Never say things like "Great question!", "Certainly!", "I hope this helps", or "Based on my knowledge".
5. Do not repeat the question back to the user.
6. When numbers are available, use them. Prefer specific figures over vague statements.
7. Structure your answer clearly: use bullet points or short paragraphs when listing multiple findings.
8. When appropriate, mention the type of source in a natural business-friendly way (e.g., internal data, reports, audience insights). Do NOT mention technical terms like SQL, CSV, or database.
9. Never output JSON, SQL code, or raw data blocks — only plain English analysis.
10. End your answer when you have addressed the question. No closing remarks.
11. Always explain WHY, not just WHAT.
12. Identify patterns, trends, or anomalies in the data.
13. If limited data is available, clearly state limitations and provide best possible insight.
14. Always explain WHY the result is happening using the data.
15. Highlight business implications (what this means for the company).
16. Prefer insights over description — avoid just listing numbers."""


def run_ai_query(question: str, conversation_history: list = None) -> dict:
    context, sources = _build_context(question)

    user_message = f"""DATA:
{context if context else "No data available for this question."}

QUESTION: {question}"""

    messages = []
    # Include prior turns for context (keep last 6 to stay within token limits)
    if conversation_history:
        for turn in conversation_history[-6:]:
            role = turn.get("role", "user")
            content = turn.get("content", "")
            if role in ("user", "assistant") and content:
                messages.append({"role": role, "content": content})
    messages.append({"role": "user", "content": user_message})

    try:
        client = _get_groq_client()
        response = client.chat.completions.create(
            model=GROQ_MODEL,          # ← ONE line to change the model
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + messages,
            temperature=0.1,           # low = factual, less hallucination
            max_tokens=1024,
        )
        answer = response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Groq API error: {e}")
        raise RuntimeError(f"AI model error: {str(e)}")

    # Clean up any accidental JSON / code blocks the model might emit
    answer = re.sub(r"```[\s\S]*?```", "", answer).strip()
    answer = re.sub(r'\{"[\s\S]*?\}', "", answer).strip()

    return {
        "answer": answer,
        "tool_calls": [],
        "sources": sources if sources else ["Sources: Internal data and business reports"],
        "conversation": (conversation_history or []) + [
            {"role": "user", "content": question},
            {"role": "assistant", "content": answer},
        ],
    }


