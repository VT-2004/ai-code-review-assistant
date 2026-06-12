import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI Code Review Assistant",
  description: "Instant AI-powered code reviews for any GitHub repository",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}