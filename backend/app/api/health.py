from fastapi import APIRouter, status

router = APIRouter(tags=["system"])


@router.get("/health", status_code=status.HTTP_200_OK)
def health_check() -> dict[str, str]:
    """Container liveness endpoint; it intentionally has no dependency checks."""
    return {"status": "ok"}
