from fastapi import APIRouter

router = APIRouter()


@router.get(
    "/health",
    summary="Health Check",
    description="Returns the health status of the API service",
    response_description="Health status with 'healthy' status when the service is operational",
)
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
