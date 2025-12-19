# Bylaw Parser API

FastAPI backend for processing bylaw PDFs with extraction and translation.

## Setup

```bash
pip install -r requirements.txt
```
if docling fails try
```
pip install --upgrade docling
```


if openAI fails
```
pip install --upgrade openai
```

Create `.env` file in the backend directory and add your OpenAI API key:
```
OPENAI_API_KEY=your-openai-api-key-here
```

## Run

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## API Endpoints

### Main Endpoint (Recommended)
`POST /api/process`
- Upload PDF file
- Automatically extracts sections and translates them
- Returns job_id and both download URLs

curl -X POST "http://localhost:8000/api/process" -F "file=@bylaw_section_parser\zoning-by-law-district-schedule-r1-1.pdf"

