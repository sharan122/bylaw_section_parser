import json
import uuid
from pathlib import Path
from typing import Dict, Any

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse

from app.services.docling_extractor import extract_sections_from_pdf
from app.routes.translate import translate_sections_from_file

router = APIRouter()

UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("outputs")
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)


@router.post("/process")
async def process_pdf(file: UploadFile = File(...), model_name: str = "gpt-4o-mini") -> Dict[str, Any]:
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    job_id = str(uuid.uuid4())
    upload_path = UPLOAD_DIR / f"{job_id}_{file.filename}"
    output_path = OUTPUT_DIR / f"{job_id}_sections.json"
    
    try:
        with upload_path.open("wb") as f:
            content = await file.read()
            f.write(content)
        
        sections = extract_sections_from_pdf(upload_path)
        
        output_data = {"sections": sections}
        with output_path.open("w", encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        upload_path.unlink()
        
        translation_result = translate_sections_from_file(job_id, model_name)
        
        return {
            "job_id": job_id,
            "status": "success",
            "sections_count": len(sections),
            "translated_count": translation_result["translated_count"],
            "download_urls": {
                "extracted": f"/api/download/extracted/{job_id}",
                "translated": f"/api/download/translated/{job_id}"
            }
        }
    except Exception as e:
        if upload_path.exists():
            upload_path.unlink()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/download/extracted/{job_id}")
async def download_extracted(job_id: str):
    file_path = OUTPUT_DIR / f"{job_id}_sections.json"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(
        file_path,
        filename="sections.json",
        media_type="application/json"
    )


@router.post("/extract")
async def extract_only(file: UploadFile = File(...)) -> Dict[str, Any]:
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    job_id = str(uuid.uuid4())
    upload_path = UPLOAD_DIR / f"{job_id}_{file.filename}"
    output_path = OUTPUT_DIR / f"{job_id}_sections.json"
    
    try:
        with upload_path.open("wb") as f:
            content = await file.read()
            f.write(content)
        
        sections = extract_sections_from_pdf(upload_path)
        
        output_data = {"sections": sections}
        with output_path.open("w", encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        upload_path.unlink()
        
        return {
            "job_id": job_id,
            "status": "success",
            "sections_count": len(sections),
            "download_url": f"/api/download/extracted/{job_id}"
        }
    except Exception as e:
        if upload_path.exists():
            upload_path.unlink()
        raise HTTPException(status_code=500, detail=str(e))

