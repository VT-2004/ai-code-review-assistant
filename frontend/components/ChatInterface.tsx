"use client";
import { useState, useRef, useEffect } from "react";
import { Send, Loader2, FileCode } from "lucide-react";
import { sendChat } from "@/lib/api";

interface Message {
  role: "user" | "assistant";
  content: string;
  sources?: string[];
}

const SUGGESTED = [
  "What are the biggest security issues?",
  "Where is error handling missing?",
  "Which functions have performance problems?",
  "How is authentication handled?",
];

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content: "I've analyzed the codebase. Ask me anything about the code — bugs, architecture, specific functions, or security concerns.",
    }
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function handleSend(text?: string) {
    const question = text || input.trim();
    if (!question || loading) return;

    setInput("");
    setMessages(prev => [...prev, { role: "user", content: question }]);
    setLoading(true);

    try {
      const res = await sendChat(question);
      setMessages(prev => [...prev, {
        role: "assistant",
        content: res.answer,
        sources: res.sources
      }]);
    } catch (e) {
      setMessages(prev => [...prev, {
        role: "assistant",
        content: "Sorry, something went wrong. Make sure a review has been run first."
      }]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="rounded-xl overflow-hidden flex flex-col"
      style={{ border: "1px solid var(--border)", background: "var(--card)", height: "65vh" }}>

      {/* messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
            <div className="max-w-[80%]">
              <div className="rounded-xl px-4 py-3 text-sm"
                style={{
                  background: msg.role === "user" ? "var(--accent)" : "var(--background)",
                  color: "var(--text-primary)",
                  border: msg.role === "assistant" ? "1px solid var(--border)" : "none"
                }}>
                {msg.content}
              </div>

              {/* source files */}
              {msg.sources && msg.sources.length > 0 && (
                <div className="flex flex-wrap gap-1.5 mt-1.5">
                  {msg.sources.map((s, j) => (
                    <span key={j} className="flex items-center gap-1 text-xs px-2 py-0.5 rounded"
                      style={{ background: "var(--border)", color: "var(--text-secondary)" }}>
                      <FileCode size={10} /> {s.split("/").pop()}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="rounded-xl px-4 py-3"
              style={{ background: "var(--background)", border: "1px solid var(--border)" }}>
              <Loader2 size={16} className="animate-spin" style={{ color: "var(--accent)" }} />
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* suggested questions */}
      {messages.length === 1 && (
        <div className="px-4 pb-2 flex flex-wrap gap-2">
          {SUGGESTED.map((q, i) => (
            <button key={i} onClick={() => handleSend(q)}
              className="text-xs px-3 py-1.5 rounded-full transition-all hover:opacity-80"
              style={{ background: "var(--border)", color: "var(--text-secondary)" }}>
              {q}
            </button>
          ))}
        </div>
      )}

      {/* input */}
      <div className="p-4 border-t flex gap-3" style={{ borderColor: "var(--border)" }}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          placeholder="Ask anything about the codebase..."
          className="flex-1 px-4 py-2.5 rounded-lg text-sm outline-none"
          style={{
            background: "var(--background)",
            border: "1px solid var(--border)",
            color: "var(--text-primary)"
          }}
        />
        <button onClick={() => handleSend()}
          disabled={!input.trim() || loading}
          className="px-4 py-2.5 rounded-lg transition-all disabled:opacity-50"
          style={{ background: "var(--accent)", color: "white" }}>
          <Send size={16} />
        </button>
      </div>
    </div>
  );
}