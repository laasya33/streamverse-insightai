import os, logging
import pandas as pd

logger = logging.getLogger(__name__)
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

TOOL_DEFINITION = {
    "name": "analyze_csv_data",
    "description": (
        "Analyze CSV business data files directly using pandas for aggregations, "
        "comparisons, and summaries. Available files: movies, viewers, watch_activity, "
        "reviews, marketing_spend, regional_performance. "
        "Use this for genre comparisons, city rankings, platform stats, and trend analysis."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "file": {
                "type": "string",
                "description": "CSV file name without extension.",
                "enum": ["movies", "viewers", "watch_activity", "reviews",
                         "marketing_spend", "regional_performance"]
            },
            "operation": {
                "type": "string",
                "description": "Analysis type: summary | top_n | filter | groupby | compare",
                "enum": ["summary", "top_n", "filter", "groupby", "compare"]
            },
            "params": {
                "type": "object",
                "description": (
                    "Operation parameters. "
                    "top_n: {column, n, ascending}. "
                    "filter: {column, value}. "
                    "groupby: {by, agg_column, agg_func}. "
                    "compare: {column, values}."
                )
            }
        },
        "required": ["file", "operation"]
    }
}

def execute(file: str, operation: str, params: dict = None) -> dict:
    params = params or {}
    path = os.path.join(os.path.abspath(DATA_DIR), f"{file}.csv")
    if not os.path.exists(path):
        return {"error": f"File {file}.csv not found", "source": "Internal data and business reports"}
    df = pd.read_csv(path)
    result = {}
    try:
        if operation == "summary":
            result = {
                "shape": df.shape,
                "columns": list(df.columns),
                "numeric_summary": df.describe().round(2).to_dict()
            }
        elif operation == "top_n":
            col = params.get("column", df.columns[0])
            n = int(params.get("n", 10))
            asc = params.get("ascending", False)
            top = df.sort_values(col, ascending=asc).head(n)
            result = {"rows": top.to_dict(orient="records")}
        elif operation == "filter":
            col = params.get("column")
            val = params.get("value")
            filtered = df[df[col].astype(str).str.lower() == str(val).lower()]
            result = {"rows": filtered.to_dict(orient="records")}
        elif operation == "groupby":
            by = params.get("by")
            agg_col = params.get("agg_column")
            agg_func = params.get("agg_func", "mean")
            grouped = df.groupby(by)[agg_col].agg(agg_func).reset_index()
            grouped.columns = [by, f"{agg_func}_{agg_col}"]
            result = {"rows": grouped.round(2).to_dict(orient="records")}
        elif operation == "compare":
            col = params.get("column")
            vals = params.get("values", [])
            filtered = df[df[col].isin(vals)]
            result = {"rows": filtered.to_dict(orient="records")}
        else:
            result = {"error": "Unknown operation"}
    except Exception as e:
        result = {"error": str(e)}

    result["source"] = "Internal data and business reports"
    result["file"] = file
    result["operation"] = operation
    logger.info(f"CSV {operation} on {file}: {result.get('error','ok')}")
    return result
