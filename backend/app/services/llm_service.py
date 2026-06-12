from groq import Groq
import json
import time
from app.core.config import GROQ_API_KEY
from app.models.schemas import FileReview, Issue

client = Groq(api_key=GROQ_API_KEY)
MODEL = "llama-3.1-8b-instant"

REVIEW_SYSTEM_PROMPT = """You are a senior software engineer with 10+ years experience doing thorough code reviews.

Analyze the provided code chunk and return ONLY a valid JSON object — no markdown, no explanation, no backticks.

Rules:
- Be specific: mention actual function names, variable names, and line references from the code
- Do NOT report issues that don't exist in this specific chunk
- Severity guide:
  * critical = security vulnerability, data loss risk, or crash-causing bug
  * high = logic error, missing error handling on critical path, or serious performance issue
  * medium = code smell, missing validation, or suboptimal pattern
  * low = style issue, naming convention, or minor improvement
- Score guide:
  * 90-100 = clean, well-written code with no significant issues
  * 75-89 = mostly good with minor improvements needed
  * 60-74 = several issues that should be addressed
  * below 60 = significant problems requiring immediate attention

JSON format:
{
  "score": <integer 0-100>,
  "summary": "<one sentence describing what this code does>",
  "issues": [
    {
      "type": "<bug|security|style|performance>",
      "severity": "<critical|high|medium|low>",
      "line_hint": "<exact function name or variable name from the code>",
      "description": "<specific description referencing actual code>",
      "suggestion": "<concrete fix with example if possible>"
    }
  ]
}

If there are no real issues, return an empty issues array. Do not invent issues."""

def review_chunk(chunk_text: str, file_path: str, language: str) -> dict:
    prompt = f"""File: {file_path}
Language: {language}

Code:
{chunk_text}

Review this code chunk."""

    for attempt in range(3):  # retry up to 3 times
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": REVIEW_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2
            )

            raw = response.choices[0].message.content.strip()

            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]

            try:
                return json.loads(raw)
            except json.JSONDecodeError:
                start = raw.find("{")
                end = raw.rfind("}") + 1
                return json.loads(raw[start:end])

        except Exception as e:
            error_str = str(e).lower()
            if "rate limit" in error_str:
                wait = 2 ** attempt
                print(f"    rate limited — waiting {wait}s before retry...")
                time.sleep(wait)
            else:
                raise e

    raise ValueError(f"Failed after 3 attempts for chunk in {file_path}")

SEVERITY_WEIGHTS = {
    "critical": 15,
    "high": 8,
    "medium": 4,
    "low": 1
}

def review_file(file_path: str, chunks: list[dict]) -> FileReview:
    all_issues = []
    raw_scores = []

    for chunk in chunks:
        try:
            result = review_chunk(chunk["text"], file_path, chunk["language"])
            raw_scores.append(result.get("score", 70))
            for issue in result.get("issues", []):
                all_issues.append(Issue(**issue))
        except Exception as e:
            print(f"    warning: chunk parse failed ({e})")
            continue

    # deduplicate issues by description similarity
    seen = set()
    unique_issues = []
    for issue in all_issues:
        # use first 60 chars of description as dedup key
        key = issue.description[:60].lower().strip()
        if key not in seen:
            seen.add(key)
            unique_issues.append(issue)

    # severity weighted score — critical issues tank the score more
    base_score = int(sum(raw_scores) / len(raw_scores)) if raw_scores else 70
    penalty = sum(SEVERITY_WEIGHTS.get(i.severity, 1) for i in unique_issues)
    final_score = max(0, min(100, base_score - penalty))

    summary = f"{len(unique_issues)} issue(s) found across {len(chunks)} chunk(s)."

    return FileReview(
        file_path=file_path,
        language=chunks[0]["language"] if chunks else "unknown",
        score=final_score,
        issues=unique_issues,
        summary=summary
    )
def chat_with_codebase(question: str, relevant_chunks: list[dict]) -> dict:
    context = "\n\n".join([
        f"File: {c['file_path']}\n{c['text']}"
        for c in relevant_chunks
    ])

    prompt = f"""You are a helpful code assistant. Answer the question based only on the code context provided.

Code context:
{context}

Question: {question}"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    sources = list(set(c["file_path"] for c in relevant_chunks))
    return {
        "answer": response.choices[0].message.content.strip(),
        "sources": sources
    }