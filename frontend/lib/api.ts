import axios from "axios";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface Issue {
  type: string;
  severity: string;
  line_hint: string;
  description: string;
  suggestion: string;
}

export interface FileReview {
  file_path: string;
  language: string;
  score: number;
  issues: Issue[];
  summary: string;
}

export interface ReviewResponse {
  repo_url: string;
  overall_score: number;
  total_files: number;
  total_issues: number;
  file_reviews: FileReview[];
  top_concerns: string[];
}

export interface ChatResponse {
  answer: string;
  sources: string[];
}

export async function runReview(repoUrl: string, maxFiles: number = 30): Promise<ReviewResponse> {
  const res = await axios.post(`${API_BASE}/api/review`, {
    repo_url: repoUrl,
    max_files: maxFiles
  });
  return res.data;
}

export async function sendChat(question: string): Promise<ChatResponse> {
  const res = await axios.post(`${API_BASE}/api/chat`, {
    question
  });
  return res.data;
}