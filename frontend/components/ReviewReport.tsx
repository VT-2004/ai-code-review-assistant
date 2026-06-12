"use client";
import React from "react";
import { ReviewResponse, FileReview, Issue } from "@/lib/api";
import { useState } from "react";
import { ChevronDown, ChevronUp, AlertTriangle, Shield, Zap, Code2 } from "lucide-react";

const SEVERITY_COLORS: Record<string, string> = {
  critical: "#ef4444",
  high:     "#f97316",
  medium:   "#eab308",
  low:      "#6366f1",
};

const TYPE_ICONS: Record<string, React.ReactElement> = {
  bug:         <AlertTriangle size={13} />,
  security:    <Shield size={13} />,
  performance: <Zap size={13} />,
  style:       <Code2 size={13} />,
};

function ScoreRing({ score }: { score: number }) {
  const color = score >= 80 ? "#22c55e" : score >= 60 ? "#eab308" : "#ef4444";
  const r = 36;
  const circ = 2 * Math.PI * r;
  const filled = (score / 100) * circ;

  return (
    <div className="flex flex-col items-center justify-center" style={{ minWidth: 100 }}>
      <svg width="100" height="100" viewBox="0 0 100 100">
        <circle cx="50" cy="50" r={r} fill="none" stroke="var(--border)" strokeWidth="8" />
        <circle cx="50" cy="50" r={r} fill="none" stroke={color} strokeWidth="8"
          strokeDasharray={`${filled} ${circ}`}
          strokeLinecap="round"
          transform="rotate(-90 50 50)" />
        <text x="50" y="54" textAnchor="middle" fontSize="18" fontWeight="bold" fill={color}>
          {score}
        </text>
      </svg>
      <span className="text-xs mt-1" style={{ color: "var(--text-secondary)" }}>overall score</span>
    </div>
  );
}

function IssueBadge({ issue }: { issue: Issue }) {
  const color = SEVERITY_COLORS[issue.severity] || "#6366f1";
  const icon = TYPE_ICONS[issue.type] || <Code2 size={13} />;

  return (
    <div className="rounded-lg p-3 mb-2"
      style={{ background: "var(--background)", border: `1px solid ${color}30` }}>
      <div className="flex items-center gap-2 mb-1">
        <span style={{ color }}>{icon}</span>
        <span className="text-xs font-semibold uppercase tracking-wide" style={{ color }}>
          {issue.severity}
        </span>
        <span className="text-xs px-2 py-0.5 rounded-full"
          style={{ background: `${color}20`, color }}>
          {issue.type}
        </span>
        <span className="text-xs ml-auto" style={{ color: "var(--text-secondary)" }}>
          {issue.line_hint}
        </span>
      </div>
      <p className="text-sm mb-1" style={{ color: "var(--text-primary)" }}>
        {issue.description}
      </p>
      <p className="text-xs" style={{ color: "var(--text-secondary)" }}>
        💡 {issue.suggestion}
      </p>
    </div>
  );
}

function FileCard({ file }: { file: FileReview }) {
  const [open, setOpen] = useState(false);
  const scoreColor = file.score >= 80 ? "#22c55e" : file.score >= 60 ? "#eab308" : "#ef4444";
  const criticalCount = file.issues.filter(i => i.severity === "critical").length;
  const highCount = file.issues.filter(i => i.severity === "high").length;

  return (
    <div className="rounded-xl mb-3 overflow-hidden"
      style={{ border: "1px solid var(--border)", background: "var(--card)" }}>

      {/* file header */}
      <div className="flex items-center gap-3 px-4 py-3 cursor-pointer hover:opacity-80"
        onClick={() => setOpen(!open)}>
        <span className="text-xs px-2 py-0.5 rounded font-mono"
          style={{ background: "var(--border)", color: "var(--text-secondary)" }}>
          {file.language}
        </span>
        <span className="text-sm font-medium flex-1 truncate"
          style={{ color: "var(--text-primary)" }}>
          {file.file_path}
        </span>

        <div className="flex items-center gap-1.5">
          {criticalCount > 0 && (
            <span className="text-xs px-2 py-0.5 rounded-full font-medium"
              style={{ background: "#ef444420", color: "#ef4444" }}>
              {criticalCount} critical
            </span>
          )}
          {highCount > 0 && (
            <span className="text-xs px-2 py-0.5 rounded-full font-medium"
              style={{ background: "#f9731620", color: "#f97316" }}>
              {highCount} high
            </span>
          )}
          <span className="text-xs px-2 py-0.5 rounded-full"
            style={{ background: `${scoreColor}20`, color: scoreColor }}>
            {file.score}/100
          </span>
        </div>

        {open ? <ChevronUp size={16} style={{ color: "var(--text-secondary)" }} />
               : <ChevronDown size={16} style={{ color: "var(--text-secondary)" }} />}
      </div>

      {/* expanded issues */}
      {open && (
        <div className="px-4 pb-4 border-t" style={{ borderColor: "var(--border)" }}>
          <p className="text-xs py-3" style={{ color: "var(--text-secondary)" }}>
            {file.summary}
          </p>
          {file.issues.length === 0 ? (
            <p className="text-sm" style={{ color: "#22c55e" }}>✓ No issues found</p>
          ) : (
            file.issues.map((issue, i) => <IssueBadge key={i} issue={issue} />)
          )}
        </div>
      )}
    </div>
  );
}

export default function ReviewReport({ review }: { review: ReviewResponse }) {
  const criticalIssues = review.file_reviews
    .flatMap(f => f.issues)
    .filter(i => i.severity === "critical").length;

  return (
    <div>
      {/* summary bar */}
      <div className="rounded-xl p-6 mb-6 flex items-center gap-8 flex-wrap"
        style={{ background: "var(--card)", border: "1px solid var(--border)" }}>
        <ScoreRing score={review.overall_score} />

        <div className="flex gap-6 flex-wrap">
          {[
            { label: "Files Reviewed", value: review.total_files },
            { label: "Total Issues", value: review.total_issues },
            { label: "Critical", value: criticalIssues, color: "#ef4444" },
          ].map(stat => (
            <div key={stat.label}>
              <div className="text-2xl font-bold"
                style={{ color: stat.color || "var(--text-primary)" }}>
                {stat.value}
              </div>
              <div className="text-xs" style={{ color: "var(--text-secondary)" }}>
                {stat.label}
              </div>
            </div>
          ))}
        </div>

        {review.top_concerns.length > 0 && (
          <div className="flex-1 min-w-48">
            <p className="text-xs font-medium mb-2" style={{ color: "var(--text-secondary)" }}>
              TOP CONCERNS
            </p>
            {review.top_concerns.slice(0, 3).map((c, i) => (
              <p key={i} className="text-xs mb-1 truncate" style={{ color: "#f97316" }}>
                • {c}
              </p>
            ))}
          </div>
        )}
      </div>

      {/* file cards */}
      <p className="text-sm font-medium mb-3" style={{ color: "var(--text-secondary)" }}>
        FILE BY FILE REVIEW
      </p>
      {review.file_reviews
        .sort((a, b) => a.score - b.score)
        .map((file, i) => <FileCard key={i} file={file} />)
      }
    </div>
  );
}