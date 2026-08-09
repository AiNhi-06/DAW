from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routers import scrape

app = FastAPI(title="Data Scraper API", version="0.1.0")

# Cho phép Streamlit (localhost:8501) gọi API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://127.0.0.1:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(scrape.router)


@app.get("/")
def root():
    return {"message": "Data Scraper API - xem tài liệu tại /docs"}
