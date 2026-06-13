from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes.review import router as review_router
from app.api.routes.chat import router as chat_router

app = FastAPI(title="AI Code Review Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(review_router, prefix="/api")
app.include_router(chat_router, prefix="/api")

@app.get("/")
def root():
    return {"status": "running"}