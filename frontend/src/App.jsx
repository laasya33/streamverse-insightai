import React, { useRef, useEffect } from "react";
import ChatMessage from "./components/ChatMessage";
import ChatInput from "./components/ChatInput";
import Charts from "./components/Charts";
import { useChat } from "./hooks/useChat";

export default function App() {
  const { messages, loading, error, sendMessage, clearChat } = useChat();
  const bottomRef = useRef();

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  return (
    <div style={{
      display: "flex", flexDirection: "column", height: "100vh",
      background: "#0f172a", color: "#f1f5f9", fontFamily: "'Inter',system-ui,sans-serif"
    }}>
      {/* Header */}
      <div style={{
        display: "flex", alignItems: "center", gap: 12,
        padding: "14px 24px", background: "#1e293b",
        borderBottom: "1px solid #334155", flexShrink: 0
      }}>
        <div style={{
          width: 36, height: 36, borderRadius: 10,
          background: "linear-gradient(135deg,#3b82f6,#8b5cf6)",
          display: "flex", alignItems: "center", justifyContent: "center", fontSize: 18
        }}>🎬</div>
        <div>
          <div style={{ fontWeight: 700, fontSize: 16 }}>StreamVerse InsightAI</div>
          <div style={{ fontSize: 11, color: "#64748b" }}>Secure Internal Analytics Assistant</div>
        </div>
      </div>

      {/* Body */}
      <div style={{ display: "flex", flex: 1, overflow: "hidden" }}>
        {/* Chat Panel */}
        <div style={{ flex: 1, display: "flex", flexDirection: "column", overflow: "hidden" }}>
          <div style={{ flex: 1, overflowY: "auto", padding: "20px 24px" }}>
            {messages.map((msg, i) => <ChatMessage key={i} message={msg} />)}
            {loading && (
              <div style={{ display: "flex", gap: 6, padding: "8px 0", alignItems: "center" }}>
                <div style={{ color: "#64748b", fontSize: 13 }}>InsightAI is thinking</div>
                {[0,1,2].map(i => (
                  <div key={i} style={{
                    width: 6, height: 6, borderRadius: "50%", background: "#3b82f6",
                    animation: `bounce 1s ease-in-out ${i*0.2}s infinite`
                  }}/>
                ))}
              </div>
            )}
            {error && (
              <div style={{
                background: "#ef444422", border: "1px solid #ef444444",
                borderRadius: 8, padding: "8px 14px", fontSize: 12, color: "#ef4444", marginBottom: 8
              }}>
                ⚠️ {error}
              </div>
            )}
            <div ref={bottomRef} />
          </div>
          <ChatInput onSend={sendMessage} loading={loading} onClear={clearChat} />
        </div>

        {/* Charts Panel */}
        <div style={{
          width: 340, borderLeft: "1px solid #334155",
          background: "#0f172a", padding: 16, overflowY: "auto", flexShrink: 0
        }}>
          <div style={{ fontSize: 12, fontWeight: 700, color: "#64748b", marginBottom: 14, textTransform: "uppercase", letterSpacing: 1 }}>
            📊 Analytics Dashboard
          </div>
          <Charts />
        </div>
      </div>

      <style>{`
        @keyframes bounce {
          0%,100%{transform:translateY(0)} 50%{transform:translateY(-4px)}
        }
        * { box-sizing: border-box; }
        ::-webkit-scrollbar { width: 4px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: #334155; border-radius: 4px; }
      `}</style>
    </div>
  );
}
