import os, logging
import pdfplumber

logger = logging.getLogger(__name__)
PDF_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "pdfs")

TOOL_DEFINITION = {
    "name": "search_pdf_documents",
    "description": (
        "Search internal StreamVerse PDF documents for qualitative insights, strategies, and reports. "
        "Available documents: quarterly_executive_report, campaign_performance_summary, "
        "content_roadmap, policy_guidelines, audience_behavior_report. "
        "Use this for questions about strategy, recommendations, campaign analysis, trends, "
        "audience behavior, and executive summaries."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "document": {
                "type": "string",
                "description": "Document name (without .pdf). Use 'all' to search all documents.",
                "enum": [
                    "quarterly_executive_report",
                    "campaign_performance_summary",
                    "content_roadmap",
                    "policy_guidelines",
                    "audience_behavior_report",
                    "all"
                ]
            },
            "query": {
                "type": "string",
                "description": "Keywords or topic to search for in the document."
            }
        },
        "required": ["document", "query"]
    }
}

def _extract_text(pdf_path: str) -> str:
    try:
        with pdfplumber.open(pdf_path) as pdf:
            return "\n".join(p.extract_text() or "" for p in pdf.pages)
    except Exception as e:
        logger.error(f"PDF read error {pdf_path}: {e}")
        return ""

def _search_text(text: str, query: str) -> list[str]:
    keywords = query.lower().split()
    results = []
    for para in text.split("\n"):
        para = para.strip()
        if para and any(kw in para.lower() for kw in keywords):
            results.append(para)
    return results[:15]

def execute(document: str, query: str) -> dict:
    pdf_dir = os.path.abspath(PDF_DIR)
    results = {}
    files = (
        [f for f in os.listdir(pdf_dir) if f.endswith(".pdf")]
        if document == "all"
        else [f"{document}.pdf"]
    )
    for fname in files:
        path = os.path.join(pdf_dir, fname)
        if not os.path.exists(path):
            continue
        text = _extract_text(path)
        matches = _search_text(text, query)
        if matches:
            results[fname.replace(".pdf", "")] = matches

    logger.info(f"PDF search '{query}' in '{document}': {len(results)} docs matched")
    return {
        "source": "Internal data and business reports",
        "query": query,
        "results": results if results else {"info": "No relevant content found."}
    }
