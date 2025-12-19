import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from openai import OpenAI

from app.prompts.translation_prompt import TRANSLATION_PROMPT

load_dotenv()


def setup_openai_client(api_key: Optional[str] = None) -> OpenAI:
    api_key = api_key or os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in .env file or environment variables")
    
    old_proxies = {}
    proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy', 'ALL_PROXY', 'all_proxy']
    
    for var in proxy_vars:
        if var in os.environ:
            old_proxies[var] = os.environ.pop(var)
    
    try:
        return OpenAI(api_key=api_key)
    finally:
        for var, value in old_proxies.items():
            os.environ[var] = value


def format_tables_for_prompt(tables: List[Dict[str, Any]]) -> str:
    if not tables:
        return ""
    
    formatted = "\n\nTables in this section:\n"
    
    for table_idx, table in enumerate(tables, 1):
        cells = table.get("cells", [])
        if not cells:
            continue
        
        formatted += f"\nTable {table_idx} (Page {table.get('page_no', '?')}):\n"
        
        rows_dict = {}
        for cell in cells:
            row = cell.get("row", 0)
            col = cell.get("col", 0)
            text = cell.get("text", "")
            
            if row not in rows_dict:
                rows_dict[row] = {}
            rows_dict[row][col] = text
        
        max_col = max((max(row_data.keys()) if row_data else 0) for row_data in rows_dict.values())
        
        for row_idx in sorted(rows_dict.keys()):
            row_data = rows_dict[row_idx]
            row_cells = []
            for col_idx in range(max_col + 1):
                row_cells.append(row_data.get(col_idx, ""))
            
            formatted += "| " + " | ".join(row_cells) + " |\n"
            
            if row_idx == min(rows_dict.keys()):
                formatted += "| " + " | ".join(["---"] * (max_col + 1)) + " |\n"
    
    return formatted


def translate_section(
    client: OpenAI,
    section_id: str,
    section_title: Optional[str],
    section_body_text: str,
    tables: List[Dict[str, Any]] = None,
    model_name: str = "gpt-4o-mini"
) -> Dict[str, Any]:
    tables_text = ""
    tables_instruction = ""
    tables_important = ""
    description_note = ""
    condition_note = ""
    requirement_note = ""
    
    if tables:
        tables_text = format_tables_for_prompt(tables)
        tables_instruction = "\nIMPORTANT: This section contains tables shown above. You MUST use the table data to inform your translation. The table information is critical for understanding conditions, requirements, and should be incorporated into your description, condition_english, and requirement_english fields."
        tables_important = "- When tables are present, you MUST incorporate their data into description, condition_english, and requirement_english. The tables contain essential regulatory information."
        description_note = " If tables are present, incorporate their key information into the summary."
        condition_note = " Use table data to identify when rules apply (e.g., different conditions for different site areas, uses, etc.)"
        requirement_note = " Use table data to specify requirements (e.g., minimum site areas, specific regulations for different uses, etc.)"
    
    prompt = TRANSLATION_PROMPT.format(
        section_id=section_id,
        section_title=section_title or "N/A",
        section_body_text=section_body_text,
        tables_text=tables_text,
        tables_instruction=tables_instruction,
        tables_important=tables_important,
        description_note=description_note,
        condition_note=condition_note,
        requirement_note=requirement_note
    )
    
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {
                    "role": "system",
                    "content": "You are a legal document translator. Return only valid JSON, no markdown or explanations."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        response_text = response.choices[0].message.content.strip()
        
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        response_text = response_text.strip()
        
        result = json.loads(response_text)
        
        return {
            "id": section_id,
            "description": result.get("description") or "",
            "condition_english": result.get("condition_english"),
            "requirement_english": result.get("requirement_english"),
            "exception": result.get("exception")
        }
    
    except json.JSONDecodeError as e:
        return {
            "id": section_id,
            "description": f"Translation error for section {section_id}",
            "condition_english": None,
            "requirement_english": None,
            "exception": None
        }
    except Exception as e:
        return {
            "id": section_id,
            "description": f"Translation error: {str(e)}",
            "condition_english": None,
            "requirement_english": None,
            "exception": None
        }

