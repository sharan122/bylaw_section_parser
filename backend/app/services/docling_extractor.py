import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from docling.document_converter import DocumentConverter

from app.utils.helpers import (
    NUMERIC_SECTION_RE,
    compute_parent_section,
    resolve_ref,
    get_page_no
)


def extract_table_summary(table_obj: Dict[str, Any]) -> Dict[str, Any]:
    page_no = get_page_no(table_obj)
    data = table_obj.get("data") or {}
    cells = data.get("table_cells") or []

    simple_cells: List[Dict[str, Any]] = []
    for cell in cells:
        simple_cells.append({
            "row": cell.get("start_row_offset_idx"),
            "col": cell.get("start_col_offset_idx"),
            "text": cell.get("text", ""),
            "column_header": cell.get("column_header", False),
            "row_header": cell.get("row_header", False),
        })

    return {
        "page_no": page_no,
        "cells": simple_cells,
    }


def parse_docling_sections(doc: Dict[str, Any]) -> List[Dict[str, Any]]:
    body = doc.get("body") or {}
    children = body.get("children") or []

    sections: List[Dict[str, Any]] = []
    current_id: Optional[str] = None
    current_title: Optional[str] = None
    body_lines: List[str] = []
    start_page: Optional[int] = None
    end_page: Optional[int] = None
    tables: List[Dict[str, Any]] = []

    def flush() -> None:
        nonlocal current_id, current_title, body_lines, start_page, end_page, tables
        if not current_id:
            return
        sections.append({
            "parent_section": compute_parent_section(current_id),
            "section": current_id,
            "section_title": current_title,
            "section_body_text": "\n".join(body_lines).strip() or None,
            "section_start_page": start_page,
            "section_end_page": end_page,
            "tables": tables or [],
        })
        current_id = None
        current_title = None
        body_lines = []
        start_page = None
        end_page = None
        tables = []

    def handle_obj(obj: Dict[str, Any]) -> None:
        nonlocal current_id, current_title, body_lines, start_page, end_page, tables

        if not obj or obj.get("content_layer", "") != "body":
            return

        if obj.get("children"):
            for child_ref in obj.get("children", []):
                ref = child_ref.get("$ref") if isinstance(child_ref, dict) else child_ref
                if not ref:
                    continue
                child_obj = resolve_ref(doc, ref)
                handle_obj(child_obj)
            return

        label = obj.get("label", "")
        data = obj.get("data") or {}
        if label == "table" or ("table_cells" in data):
            table_summary = extract_table_summary(obj)
            if current_id:
                tables.append(table_summary)
                page = table_summary.get("page_no")
                if page is not None:
                    start_page = page if start_page is None else min(start_page, page)
                    end_page = page if end_page is None else max(end_page, page)
            return

        text = (obj.get("text") or "").strip()
        if text:
            m = NUMERIC_SECTION_RE.match(text)
            if m:
                flush()
                current_id = m.group(1)
                trailing = m.group(2).strip()
                current_title = trailing or None
                page = get_page_no(obj)
                start_page = page
                end_page = page
                return

            if current_id:
                body_lines.append(text)
                page = get_page_no(obj)
                if page is not None:
                    start_page = page if start_page is None else min(start_page, page)
                    end_page = page if end_page is None else max(end_page, page)

    for child in children:
        ref = child.get("$ref")
        if not ref:
            continue
        obj = resolve_ref(doc, ref)
        handle_obj(obj)

    flush()
    return sections


def extract_sections_from_pdf(pdf_path: Path) -> List[Dict[str, Any]]:
    converter = DocumentConverter()
    result = converter.convert(str(pdf_path))
    doc = result.document
    doc_dict: Dict[str, Any] = doc.export_to_dict()
    sections = parse_docling_sections(doc_dict)
    return sections

