import React, { useState } from "react";

function renderMarkdown(text) {
  return text
    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
    .replace(/\*(.*?)\*/g, "<em>$1</em>")
    .replace(/`(.*?)`/g, "<code style='background:#1e293b;padding:2px 6px;border-radius:4px;font-size:0.85em'>$1</code>")
    .replace(/\n/g, "<br/>");
}

const SOURCE_COLORS = {
  "Internal data and business reports": "#3b82f6",
  "Internal data and business reports": "#8b5cf6",
  "Internal data and business reports": "#10b981",
};

const TOOL_ICONS = {
  "query_sql_database": "🗄️",
  "search_pdf_documents": "📄",
  "analyze_csv_data": "📊",
};

export default function ChatMessage({ message }) {
  const [showTrace, setShowTrace] = useState(false);
  const isUser = message.role === "user";

  return (
    <div style={{ display: "flex", justifyContent: isUser ? "flex-end" : "flex-start", marginBottom: 16 }}>
      <div style={{ maxWidth: "78%", display: "flex", flexDirection: "column", gap: 6 }}>
        {!isUser && (
          <div style={{ fontSize: 11, color: "#94a3b8", marginLeft: 4 }}>InsightAI</div>
        )}
        <div style={{
          background: isUser ? "linear-gradient(135deg,#3b82f6,#6366f1)" : "#1e293b",
          color: "#f1f5f9",
          padding: "12px 16px",
          borderRadius: isUser ? "18px 18px 4px 18px" : "18px 18px 18px 4px",
          fontSize: 14,
          lineHeight: 1.7,
          border: isUser ? "none" : "1px solid #334155",
        }}
          dangerouslySetInnerHTML={{ __html: renderMarkdown(message.content) }}
        />

        {!isUser && message.sources && message.sources.length > 0 && (
          <div style={{ display: "flex", gap: 6, flexWrap: "wrap", marginLeft: 4 }}>
            {message.sources.map(src => (
              <span key={src} style={{
                fontSize: 10, padding: "2px 8px", borderRadius: 12,
                background: SOURCE_COLORS[src] + "22",
                color: SOURCE_COLORS[src],
                border: `1px solid ${SOURCE_COLORS[src]}44`,
                fontWeight: 600
              }}>
                {src}
              </span>
            ))}
          </div>
        )}

        {!isUser && message.toolCalls && message.toolCalls.length > 0 && (
          <div style={{ marginLeft: 4 }}>
            <button onClick={() => setShowTrace(p => !p)} style={{
              background: "none", border: "1px solid #334155", color: "#64748b",
              fontSize: 10, padding: "2px 8px", borderRadius: 8, cursor: "pointer"
            }}>
              {showTrace ? "▲" : "▼"} Tool Trace ({message.toolCalls.length} calls)
            </button>
            {showTrace && (
              <div style={{ marginTop: 6, display: "flex", flexDirection: "column", gap: 4 }}>
                {message.toolCalls.map((tc, i) => (
                  <div key={i} style={{
                    background: "#0f172a", border: "1px solid #1e293b",
                    borderRadius: 8, padding: "8px 12px", fontSize: 11
                  }}>
                    <div style={{ color: "#38bdf8", marginBottom: 4 }}>
                      {TOOL_ICONS[tc.tool] || "🔧"} <strong>{tc.tool}</strong>
                    </div>
                    <div style={{ color: "#94a3b8" }}>
                      Input: <code>{JSON.stringify(tc.input).slice(0, 120)}</code>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
