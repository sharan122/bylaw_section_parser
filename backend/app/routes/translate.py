import json
import time
from pathlib import Path
from typing import Dict, Any, List

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.services.openai_translator import setup_openai_client, translate_section

router = APIRouter()

OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)


def translate_sections_from_file(job_id: str, model_name: str = "gpt-4o-mini") -> Dict[str, Any]:
    sections_file = OUTPUT_DIR / f"{job_id}_sections.json"
    if not sections_file.exists():
        raise FileNotFoundError("Sections file not found")
    
    with sections_file.open("r", encoding="utf-8") as f:
        data = json.load(f)
    
    sections = data.get("sections", [])
    sections_with_text = [
        s for s in sections
        if s.get("section_body_text") and s["section_body_text"].strip()
    ]
    
    sections_with_tables = [
        s for s in sections
        if s.get("tables") and len(s.get("tables", [])) > 0
    ]
    
    all_sections_to_translate = list({s.get("section"): s for s in sections_with_text + sections_with_tables}.values())
    
    client = setup_openai_client()
    translated_sections: List[Dict[str, Any]] = []
    
    for i, section in enumerate(all_sections_to_translate, 1):
        section_id = section.get("section", "")
        section_title = section.get("section_title")
        section_body_text = section.get("section_body_text", "")
        tables = section.get("tables", [])
        
        translated = translate_section(
            client=client,
            section_id=section_id,
            section_title=section_title,
            section_body_text=section_body_text or "",
            tables=tables,
            model_name=model_name
        )
        
        translated_sections.append(translated)
        
        if i < len(all_sections_to_translate):
            time.sleep(0.5)
    
    output_path = OUTPUT_DIR / f"{job_id}_translated.json"
    output_data = {"translated_sections": translated_sections}
    
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    return {
        "job_id": job_id,
        "status": "success",
        "translated_count": len(translated_sections),
        "download_url": f"/api/download/translated/{job_id}"
    }


@router.post("/translate/{job_id}")
async def translate_sections(job_id: str, model_name: str = "gpt-4o-mini") -> Dict[str, Any]:
    try:
        return translate_sections_from_file(job_id, model_name)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Sections file not found. Extract sections first.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/download/translated/{job_id}")
async def download_translated(job_id: str):
    file_path = OUTPUT_DIR / f"{job_id}_translated.json"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(
        file_path,
        filename="translated_sections.json",
        media_type="application/json"
    )

