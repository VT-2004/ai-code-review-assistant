"use client";
import { useState } from "react";
import { GitBranch, Loader2, Zap, Shield, Code2, TrendingUp } from "lucide-react";
import { runReview, ReviewResponse } from "@/lib/api";
import ReviewReport from "@/components/ReviewReport";
import ChatInterface from "@/components/ChatInterface";

export default function Home() {
  const [repoUrl, setRepoUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [review, setReview] = useState<ReviewResponse | null>(null);
  const [error, setError] = useState("");
  const [showChat, setShowChat] = useState(false);

  async function handleReview() {
    if (!repoUrl.trim()) return;
    setLoading(true);
    setError("");
    setReview(null);

    try {
      const result = await runReview(repoUrl, 20);
      setReview(result);
    } catch (e: any) {
      const detail = e?.response?.data?.detail;
      if (typeof detail === "string") {
        setError(detail);
      } else if (e?.message?.includes("Network Error")) {
        setError("Cannot reach the backend. Make sure the FastAPI server is running on port 8000.");
      } else {
        setError("Something went wrong. Check the repo URL and try again.");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen" style={{ background: "var(--background)" }}>

      {/* header */}
      <header className="border-b px-6 py-4 flex items-center justify-between"
        style={{ borderColor: "var(--border)", background: "var(--card)" }}>
        <div className="flex items-center gap-2">
          <Code2 size={22} style={{ color: "var(--accent)" }} />
          <span className="font-semibold text-lg" style={{ color: "var(--text-primary)" }}>
            CodeReview<span style={{ color: "var(--accent)" }}>AI</span>
          </span>
        </div>
        {review && (
          <button
            onClick={() => setShowChat(!showChat)}
            className="text-sm px-4 py-2 rounded-lg font-medium transition-all"
            style={{
              background: showChat ? "var(--accent)" : "var(--border)",
              color: "var(--text-primary)"
            }}>
            {showChat ? "View Report" : "Chat with Codebase"}
          </button>
        )}
      </header>

      <div className="max-w-5xl mx-auto px-6 py-12">

        {/* hero */}
        {!review && !loading && (
          <div className="text-center mb-12">
            <h1 className="text-4xl font-bold mb-4" style={{ color: "var(--text-primary)" }}>
              AI-Powered Code Review
            </h1>
            <p className="text-lg mb-2" style={{ color: "var(--text-secondary)" }}>
              Paste any public GitHub repository URL and get an instant senior engineer review.
            </p>
            <div className="flex flex-wrap justify-center gap-3 mt-6">
              {[
                { icon: <Shield size={14} />, label: "Security Vulnerabilities" },
                { icon: <Zap size={14} />, label: "Performance Issues" },
                { icon: <Code2 size={14} />, label: "Code Quality" },
                { icon: <TrendingUp size={14} />, label: "Best Practices" },
              ].map((f) => (
                <span key={f.label} className="flex items-center gap-1.5 text-sm px-3 py-1.5 rounded-full"
                  style={{ background: "var(--card)", border: "1px solid var(--border)", color: "var(--text-secondary)" }}>
                  {f.icon}{f.label}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* input box */}
        <div className="rounded-xl p-6 mb-8"
          style={{ background: "var(--card)", border: "1px solid var(--border)" }}>
          <label className="block text-sm font-medium mb-2" style={{ color: "var(--text-secondary)" }}>
            GitHub Repository URL
          </label>
          <div className="flex gap-3">
            <div className="flex-1 flex items-center gap-3 px-4 rounded-lg"
              style={{ background: "var(--background)", border: "1px solid var(--border)" }}>
              <GitBranch size={18} style={{ color: "var(--text-secondary)" }} />
              <input
                type="text"
                value={repoUrl}
                onChange={(e) => setRepoUrl(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleReview()}
                placeholder="https://github.com/owner/repository"
                className="flex-1 bg-transparent py-3 text-sm outline-none"
                style={{ color: "var(--text-primary)" }}
              />
            </div>
            <button
              onClick={handleReview}
              disabled={loading || !repoUrl.trim()}
              className="px-6 py-3 rounded-lg font-medium text-sm transition-all disabled:opacity-50"
              style={{ background: "var(--accent)", color: "white" }}>
              {loading ? (
                <span className="flex items-center gap-2">
                  <Loader2 size={16} className="animate-spin" /> Analyzing...
                </span>
              ) : "Review Code"}
            </button>
          </div>

          {error && (
            <p className="mt-3 text-sm" style={{ color: "#f87171" }}>{error}</p>
          )}
        </div>

        {/* loading state */}
        {loading && (
          <div className="text-center py-16">
            <Loader2 size={40} className="animate-spin mx-auto mb-4" style={{ color: "var(--accent)" }} />
            <p className="text-lg font-medium mb-2" style={{ color: "var(--text-primary)" }}>
              Analyzing repository...
            </p>
            <p className="text-sm" style={{ color: "var(--text-secondary)" }}>
              Fetching files → chunking → embedding → reviewing with AI
            </p>
          </div>
        )}

        {/* results */}
        {review && !loading && (
          showChat
            ? <ChatInterface />
            : <ReviewReport review={review} />
        )}

      </div>
    </main>
  );
}