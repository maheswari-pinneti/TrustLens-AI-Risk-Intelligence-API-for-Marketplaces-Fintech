"""
Listing Risk Analysis API Endpoints
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from PIL import Image
from app.database.connection import get_db
from app.api.schemas.request import AnalyzeListingRequest, BatchAnalyzeRequest
from app.api.schemas.response import AnalyzeResponse, BatchAnalyzeResponse, ImageCheckResponse
from app.services.analysis_service import AnalysisService
from app.security.rate_limiter import check_rate_limit
from app.detectors.image_checker import ImageChecker

router = APIRouter(prefix="/analyze", tags=["Risk Analysis Engine"], dependencies=[Depends(check_rate_limit)])


@router.post(
    "",
    response_model=AnalyzeResponse,
    summary="Analyze Product Listing for Fraud Risk",
    description="Evaluates price anomalies, counterfeit keywords, image similarity, and seller risk factors."
)
def analyze_listing(
    request: AnalyzeListingRequest,
    persist: bool = Query(default=True, description="Whether to store the analyzed listing in the database for tracking"),
    db: Session = Depends(get_db)
):
    service = AnalysisService(db)
    return service.analyze_listing(request, persist=persist)


@router.post(
    "/batch",
    response_model=BatchAnalyzeResponse,
    summary="Batch Analyze Multiple Listings",
    description="Analyzes up to 100 listings concurrently with aggregate risk statistics."
)
def analyze_batch(
    request: BatchAnalyzeRequest,
    persist: bool = Query(default=True, description="Persist listings to audit database"),
    db: Session = Depends(get_db)
):
    service = AnalysisService(db)
    return service.analyze_batch(request, persist=persist)


@router.post(
    "/image",
    response_model=ImageCheckResponse,
    summary="Upload & Inspect Product Image for Duplication",
    description="Generates perceptual hashes and compares against known marketplace image fingerprints."
)
def check_image(
    file: UploadFile = File(..., description="Product image file (JPEG, PNG, WebP)"),
    db: Session = Depends(get_db)
):
    service = AnalysisService(db)
    try:
        content = file.file.read()
        if len(content) > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Image file exceeds 10MB limit")

        if not ImageChecker.validate_image_magic_bytes(content):
            raise HTTPException(
                status_code=400,
                detail="Invalid image format. Uploaded file magic bytes do not match JPEG, PNG, WebP, or GIF."
            )
        
        import io
        img = Image.open(io.BytesIO(content)).convert("RGB")
        hashes = ImageChecker.compute_hashes(img)
        analysis = service.image_checker.analyze(image_input=img)

        return ImageCheckResponse(
            image_hash=hashes["primary_hash"],
            perceptual_hash=hashes["phash"],
            is_duplicate=analysis["is_duplicate"],
            duplicate_listing_id=analysis["matches"][0]["source_id"] if analysis["matches"] else None,
            similarity_score=analysis["similarity_score"],
            flags=analysis["flags"]
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to process image: {str(e)}")
