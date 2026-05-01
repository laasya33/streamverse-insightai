import React, { useState, useRef } from "react";

const SUGGESTED = [
  "Which titles performed best in 2025?",
  "Why is Stellar Run trending recently?",
  "Compare Dark Orbit vs Last Kingdom",
  "Which city had the strongest engagement last month?",
  "What explains weak comedy performance?",
  "What recommendations would you give for leadership?",
];

export default function ChatInput({ onSend, loading, onClear }) {
  const [value, setValue] = useState("");
  const ref = useRef();

  const submit = () => {
    if (!value.trim() || loading) return;
    onSend(value.trim());
    setValue("");
    ref.current?.focus();
  };

  const handleKey = (e) => {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); submit(); }
  };

  return (
    <div style={{ padding: "12px 20px 20px", background: "#0f172a", borderTop: "1px solid #1e293b" }}>
      <div style={{ display: "flex", flexWrap: "wrap", gap: 6, marginBottom: 10 }}>
        {SUGGESTED.map(s => (
          <button key={s} onClick={() => { setValue(s); ref.current?.focus(); }}
            style={{
              fontSize: 11, padding: "4px 10px", borderRadius: 12,
              background: "#1e293b", color: "#94a3b8",
              border: "1px solid #334155", cursor: "pointer",
              transition: "all 0.2s"
            }}
            onMouseOver={e => e.target.style.color = "#38bdf8"}
            onMouseOut={e => e.target.style.color = "#94a3b8"}
          >{s}</button>
        ))}
      </div>
      <div style={{ display: "flex", gap: 8 }}>
        <textarea ref={ref} value={value} onChange={e => setValue(e.target.value)}
          onKeyDown={handleKey} rows={2} placeholder="Ask a business question..."
          style={{
            flex: 1, background: "#1e293b", border: "1px solid #334155",
            borderRadius: 12, color: "#f1f5f9", padding: "10px 14px",
            fontSize: 14, resize: "none", outline: "none", fontFamily: "inherit"
          }}
        />
        <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
          <button onClick={submit} disabled={loading || !value.trim()} style={{
            background: loading ? "#334155" : "linear-gradient(135deg,#3b82f6,#6366f1)",
            color: "white", border: "none", borderRadius: 10,
            padding: "10px 18px", cursor: loading ? "not-allowed" : "pointer",
            fontSize: 13, fontWeight: 600, flex: 1
          }}>
            {loading ? "..." : "Send"}
          </button>
          <button onClick={onClear} style={{
            background: "#1e293b", color: "#64748b", border: "1px solid #334155",
            borderRadius: 10, padding: "6px 10px", cursor: "pointer", fontSize: 11
          }}>Clear</button>
        </div>
      </div>
    </div>
  );
}
