import re
from typing import Dict, Any, Optional


NUMERIC_SECTION_RE = re.compile(r"^(\d+(?:\.\d+)*)\s*(.*)$")


def compute_parent_section(section_id: str) -> str:
    parts = section_id.split(".")
    return ".".join(parts[:-1]) if len(parts) > 1 else ""


def resolve_ref(doc: Dict[str, Any], ref: str) -> Dict[str, Any]:
    if not ref.startswith("#/"):
        raise ValueError(f"Unsupported ref format: {ref}")
    path = ref[2:].split("/")
    obj: Any = doc
    for part in path:
        if isinstance(obj, list):
            idx = int(part)
            obj = obj[idx]
        else:
            obj = obj[part]
    return obj


def get_page_no(obj: Dict[str, Any]) -> Optional[int]:
    prov = obj.get("prov") or []
    if prov and isinstance(prov, list):
        page = prov[0].get("page_no")
        if isinstance(page, int):
            return page
    return None

