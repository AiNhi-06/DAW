from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["scrape"])


@router.get("/health")
def health():
    return {"status": "ok"}
