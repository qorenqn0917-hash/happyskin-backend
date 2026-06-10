from fastapi import APIRouter, Depends, File, Form, UploadFile

from app.dependencies import verify_api_key
from app.schemas.analysis import SkinReportResponse
from app.services.ai_service import AIService
from app.services.image_service import ImageService
from app.db.repositories.analysis_repo import AnalysisRepository

router = APIRouter(dependencies=[Depends(verify_api_key)])


@router.post("/", response_model=SkinReportResponse, status_code=201)
async def analyze_skin(
    image: UploadFile = File(...),
    device_id: str = Form(...),
    skin_type: str = Form(default="unknown"),
    concerns: str = Form(default=""),
):
    image_data = await ImageService.validate_and_compress(image)
    report = await AIService.analyze(image_data, skin_type=skin_type, concerns=concerns)
    saved = await AnalysisRepository.save(device_id=device_id, report=report, image_data=image_data)
    return saved
