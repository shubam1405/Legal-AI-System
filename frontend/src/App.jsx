import { useState, useRef, useEffect, useCallback } from "react";
import ReactMarkdown from "react-markdown";
import {
  Send,
  Upload,
  Scale,
  MessageSquare,
  FileText,
  Plus,
  Loader2,
  CheckCircle2,
  AlertCircle,
  BookOpen,
  Search,
  Gavel,
  X,
  Trash2,
  Paperclip,
} from "lucide-react";
import { sendMessage, uploadCase } from "./api";
import InsightsPanel from "./InsightsPanel";
import "./App.css";

function generateId() {
  return crypto.randomUUID?.() || Math.random().toString(36).slice(2);
}

/* ---- localStorage helpers ---- */
const HISTORY_KEY = "legal-ai-history";

function loadHistory() {
  try {
    return JSON.parse(localStorage.getItem(HISTORY_KEY)) || [];
  } catch {
    return [];
  }
}

function saveHistory(history) {
  localStorage.setItem(HISTORY_KEY, JSON.stringify(history));
}

export default function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [threadId, setThreadId] = useState(generateId);
  const [loading, setLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [chatHistory, setChatHistory] = useState(loadHistory);

  const [uploadStatus, setUploadStatus] = useState(null);
  const [uploadResult, setUploadResult] = useState(null);
  const [insightsData, setInsightsData] = useState(null);
  const [showInsights, setShowInsights] = useState(false);
  const fileRef = useRef(null);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  /* Persist history whenever it changes */
  useEffect(() => {
    saveHistory(chatHistory);
  }, [chatHistory]);

  /* Update history entry for the active thread */
  const syncToHistory = useCallback(
    (msgs) => {
      if (msgs.length === 0) return;
      const firstUserMsg = msgs.find((m) => m.role === "user");
      const title = firstUserMsg
        ? firstUserMsg.content.slice(0, 60)
        : "New chat";
      setChatHistory((prev) => {
        const idx = prev.findIndex((h) => h.id === threadId);
        const entry = {
          id: threadId,
          title,
          updatedAt: Date.now(),
          messages: msgs,
        };
        if (idx >= 0) {
          const next = [...prev];
          next[idx] = entry;
          return next;
        }
        return [entry, ...prev];
      });
    },
    [threadId]
  );

  async function handleSend(e) {
    e?.preventDefault();
    const text = input.trim();
    if (!text || loading) return;

    const userMsg = { role: "user", content: text };
    const nextMsgs = [...messages, userMsg];
    setMessages(nextMsgs);
    syncToHistory(nextMsgs);
    setInput("");
    setLoading(true);
    try {
      const data = await sendMessage(text, threadId);
      const withReply = [
        ...nextMsgs,
        { role: "assistant", content: data.answer },
      ];
      setMessages(withReply);
      syncToHistory(withReply);
    } catch (err) {
      const withErr = [
        ...nextMsgs,
        { role: "assistant", content: `Error: ${err.message}` },
      ];
      setMessages(withErr);
      syncToHistory(withErr);
    } finally {
      setLoading(false);
    }
  }

  async function handleUpload(e) {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploadStatus("uploading");
    setUploadResult(null);
    setInsightsData(null);
    setShowInsights(false);
    try {
      const result = await uploadCase(file, threadId);
      setUploadStatus("success");
      setUploadResult(result);
      if (result.insights) {
        setInsightsData(result.insights);
        setShowInsights(true);
      }
    } catch {
      setUploadStatus("error");
    }
    if (fileRef.current) fileRef.current.value = "";
  }

  function handleNewChat() {
    setMessages([]);
    setThreadId(generateId());
    setUploadStatus(null);
    setUploadResult(null);
    setInsightsData(null);
    setShowInsights(false);
  }

  function handleSelectChat(entry) {
    setMessages(entry.messages);
    setThreadId(entry.id);
    setUploadStatus(null);
    setUploadResult(null);
    setInsightsData(null);
    setShowInsights(false);
  }

  function handleDeleteChat(e, id) {
    e.stopPropagation();
    setChatHistory((prev) => prev.filter((h) => h.id !== id));
    if (id === threadId) handleNewChat();
  }

  const suggestions = [
    { icon: <Search size={18} />, text: "Find similar cases to a theft dispute" },
    { icon: <Gavel size={18} />, text: "Explain IPC Section 302" },
    { icon: <BookOpen size={18} />, text: "Summarize the uploaded judgment" },
    { icon: <FileText size={18} />, text: "What precedents are cited?" },
  ];

  return (
    <div className="app">
      {/* ===== Sidebar ===== */}
      <aside className={`sidebar ${sidebarOpen ? "open" : "closed"}`}>
        <div className="sidebar-header">
          <Scale size={28} className="logo-icon" />
          <span className="logo-text">Legal AI</span>
          <button className="close-btn" onClick={() => setSidebarOpen(false)}>
            <X size={20} />
          </button>
        </div>

        <button className="new-chat-btn" onClick={handleNewChat}>
          <Plus size={18} /> New Chat
        </button>

        <div className="sidebar-section thread-info">
          <h4>Chat History</h4>
          <div className="chat-history-list">
            {chatHistory.length === 0 ? (
              <p className="no-history">No conversations yet</p>
            ) : (
              chatHistory
                .sort((a, b) => b.updatedAt - a.updatedAt)
                .map((entry) => (
                  <button
                    key={entry.id}
                    className={`chat-history-item ${
                      entry.id === threadId ? "active" : ""
                    }`}
                    onClick={() => handleSelectChat(entry)}
                  >
                    <MessageSquare size={15} className="history-icon" />
                    <span className="history-title">{entry.title}</span>
                    <span
                      className="history-delete"
                      onClick={(e) => handleDeleteChat(e, entry.id)}
                    >
                      <Trash2 size={14} />
                    </span>
                  </button>
                ))
            )}
          </div>
        </div>

        <div className="sidebar-footer">
          <p>Powered by LangGraph + Ollama</p>
        </div>
      </aside>

      {/* ===== Main Panel ===== */}
      <main className="main">
        <header className="topbar">
          {!sidebarOpen && (
            <button className="menu-btn" onClick={() => setSidebarOpen(true)}>
              <MessageSquare size={20} />
            </button>
          )}
          <h1>
            <Scale size={22} /> Legal Research Assistant
          </h1>
        </header>

        <div className="chat-area">
          {showInsights && insightsData ? (
            <InsightsPanel
              data={insightsData}
              onClose={() => setShowInsights(false)}
            />
          ) : messages.length === 0 && !loading ? (
            <div className="empty-state">
              <Scale size={56} className="empty-icon" />
              <h2>How can I help you today?</h2>
              <p>
                Ask about uploaded judgments, legal precedents, IPC sections, or
                Indian case law.
              </p>
              <div className="suggestions">
                {suggestions.map((s, i) => (
                  <button
                    key={i}
                    className="suggestion-chip"
                    onClick={() => setInput(s.text)}
                  >
                    {s.icon}
                    {s.text}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div className="messages">
              {messages.map((m, i) => (
                <div key={i} className={`msg ${m.role}`}>
                  <div className="msg-avatar">
                    {m.role === "user" ? "You" : <Scale size={18} />}
                  </div>
                  <div className="msg-body">
                    <ReactMarkdown>{m.content}</ReactMarkdown>
                  </div>
                </div>
              ))}
              {loading && (
                <div className="msg assistant">
                  <div className="msg-avatar">
                    <Scale size={18} />
                  </div>
                  <div className="msg-body typing">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              )}
              <div ref={bottomRef} />
            </div>
          )}
        </div>

        {/* Upload status banner */}
        {uploadStatus && (
          <div className={`upload-banner ${uploadStatus}`}>  
            {uploadStatus === "uploading" && (
              <><Loader2 size={15} className="spin" /> Processing PDF…</>
            )}
            {uploadStatus === "success" && uploadResult && (
              <>
                <CheckCircle2 size={15} />
                <strong>{uploadResult.filename}</strong> — {uploadResult.chunks_created} chunks indexed
                {uploadResult.citations_found?.length > 0 && (
                  <span> · {uploadResult.citations_found.length} citations</span>
                )}
                {insightsData && !showInsights && (
                  <button className="show-insights-btn" onClick={() => setShowInsights(true)}>
                    View Insights
                  </button>
                )}
              </>
            )}
            {uploadStatus === "error" && (
              <><AlertCircle size={15} /> Upload failed. Try again.</>
            )}
          </div>
        )}

        <form className="input-bar" onSubmit={handleSend}>
          <label className="upload-input-btn" title="Upload PDF">
            <Paperclip size={20} />
            <input
              ref={fileRef}
              type="file"
              accept=".pdf"
              onChange={handleUpload}
              hidden
            />
          </label>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask a legal question…"
            disabled={loading}
          />
          <button type="submit" disabled={loading || !input.trim()}>
            {loading ? (
              <Loader2 size={20} className="spin" />
            ) : (
              <Send size={20} />
            )}
          </button>
        </form>
      </main>
    </div>
  );
}
