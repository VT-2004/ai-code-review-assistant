import numpy as np
from fastapi import APIRouter, HTTPException
from app.models.schemas import ReviewRequest, ReviewResponse
from app.services.github_service import fetch_repo
from app.services.chunker import chunk_all_files
from app.services.embedder import embed_chunks
from app.services.vector_store import store_chunks
from app.services.llm_service import review_file
from collections import defaultdict

router = APIRouter()

MAX_CHUNKS_PER_FILE = 10

@router.post("/review", response_model=ReviewResponse)
def run_review(request: ReviewRequest):
    try:
        print(f"\nStarting review: {request.repo_url}")
        files = fetch_repo(request.repo_url, max_files=request.max_files)
        if not files:
            raise HTTPException(status_code=400, detail="No code files found in repo")

        chunks = chunk_all_files(files)
        embedded = embed_chunks(chunks)
        store_chunks(embedded)

        # group chunks by file
        file_chunks = defaultdict(list)
        for chunk in chunks:
            file_chunks[chunk["file_path"]].append(chunk)

        # review each file with evenly sampled chunks
        file_reviews = []
        for file_path, f_chunks in file_chunks.items():
            if not f_chunks:
                continue

            if len(f_chunks) > MAX_CHUNKS_PER_FILE:
                indices = np.linspace(0, len(f_chunks) - 1, MAX_CHUNKS_PER_FILE, dtype=int)
                capped = [f_chunks[i] for i in indices]
            else:
                capped = f_chunks

            print(f"  reviewing: {file_path} ({len(capped)}/{len(f_chunks)} chunks)")
            review = review_file(file_path, capped)
            file_reviews.append(review)

        # weighted overall score — larger files weighted more
        if file_reviews:
            total_chunks = sum(
                len(file_chunks.get(r.file_path, [])) for r in file_reviews
            )
            weighted_score = sum(
                r.score * len(file_chunks.get(r.file_path, [1]))
                for r in file_reviews
            )
            overall_score = int(weighted_score / total_chunks) if total_chunks else 0
        else:
            overall_score = 0

        all_issues = [issue for r in file_reviews for issue in r.issues]

        # top concerns — critical first then high
        critical = [i.description[:80] for i in all_issues if i.severity == "critical"]
        high = [i.description[:80] for i in all_issues if i.severity == "high"]
        top_concerns = list(dict.fromkeys(critical + high))[:5]

        return ReviewResponse(
            repo_url=request.repo_url,
            overall_score=overall_score,
            total_files=len(file_reviews),
            total_issues=len(all_issues),
            file_reviews=file_reviews,
            top_concerns=top_concerns
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))