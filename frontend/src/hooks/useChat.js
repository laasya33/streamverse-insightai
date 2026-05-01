import { useState, useCallback } from "react";

const API_BASE = process.env.REACT_APP_API_URL || "http://localhost:8000";
const API_KEY = process.env.REACT_APP_API_SECRET_KEY;

export function useChat() {
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content: "👋 Hello! I'm **InsightAI**, StreamVerse's internal analytics assistant. Ask me anything about our movies, viewership, regional performance, or marketing data!",
      sources: [],
      toolCalls: [],
    }
  ]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [conversationHistory, setConversationHistory] = useState([]);

  const sendMessage = useCallback(async (question) => {
    setError(null);
    const userMsg = { role: "user", content: question, sources: [], toolCalls: [] };
    setMessages(prev => [...prev, userMsg]);
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/chat/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-API-Key": API_KEY        // ← only line added
        },
        body: JSON.stringify({ question, conversation_history: conversationHistory })
      });
      if (!res.ok) throw new Error(`Server error: ${res.status}`);
      const data = await res.json();
      setConversationHistory(data.conversation || []);
      setMessages(prev => [...prev, {
        role: "assistant",
        content: data.answer,
        sources: data.sources || [],
        toolCalls: data.tool_calls || []
      }]);
    } catch (err) {
      setError(err.message);
      setMessages(prev => [...prev, {
        role: "assistant",
        content: "Sorry, I encountered an error. Please try again.",
        sources: [],
        toolCalls: []
      }]);
    } finally {
      setLoading(false);
    }
  }, [conversationHistory]);

  const clearChat = useCallback(() => {
    setMessages([{
      role: "assistant",
      content: "👋 Hello! I'm **InsightAI**. Ask me anything about StreamVerse data!",
      sources: [],
      toolCalls: [],
    }]);
    setConversationHistory([]);
    setError(null);
  }, []);

  return { messages, loading, error, sendMessage, clearChat };
}