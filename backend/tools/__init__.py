from .sql_tool import TOOL_DEFINITION as SQL_TOOL, execute as sql_execute
from .pdf_tool import TOOL_DEFINITION as PDF_TOOL, execute as pdf_execute
from .csv_tool import TOOL_DEFINITION as CSV_TOOL, execute as csv_execute

ALL_TOOLS = [SQL_TOOL, PDF_TOOL, CSV_TOOL]

def dispatch_tool(name: str, inputs: dict) -> dict:
    if name == "query_sql_database":
        return sql_execute(**inputs)
    elif name == "search_pdf_documents":
        return pdf_execute(**inputs)
    elif name == "analyze_csv_data":
        return csv_execute(**inputs)
    else:
        return {"error": f"Unknown tool: {name}"}
