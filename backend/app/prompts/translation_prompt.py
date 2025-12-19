TRANSLATION_PROMPT = """You are a legal document translator. Convert this bylaw section into plain English components.

Section ID: {section_id}
Section Title: {section_title}
Section Text:
{section_body_text}
{tables_text}

{tables_instruction}

Extract and return ONLY a valid JSON object with these exact fields:
{{
  "description": "A plain English summary of the entire section, readable by a regular person (not legal jargon).{description_note}",
  "condition_english": "When does this rule apply? What triggers this section?{condition_note} If not applicable, use null.",
  "requirement_english": "What must someone actually do to comply? What are the specific requirements?{requirement_note} If not applicable, use null.",
  "exception": {{
    "condition_english": "Under what circumstances can the requirement be changed?",
    "requirement_english": "What happens if the exception applies?"
  }} OR null if no exception exists
}}

IMPORTANT:
- Return ONLY valid JSON, no markdown, no code blocks, no explanations
- Use null (not "null" string) for fields that don't apply
- If there's no exception clause, set "exception" to null
- Keep descriptions clear and concise
- Focus on actionable requirements when present
{tables_important}

JSON:"""

