# Bylaw Section Parser & Translator

A production-ready web application that processes zoning bylaw PDFs, extracts structured sections, and translates them into plain English using AI.

## Project Structure

```
bylaw_section_parser/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── main.py      # FastAPI entry point
│   │   ├── routes/      # API endpoints
│   │   ├── services/     # Business logic (extraction, translation)
│   │   ├── prompts/     # LLM prompt templates
│   │   └── utils/       # Helper functions
│   └── requirements.txt
├── frontend/             # React + Vite frontend
│   ├── src/
│   │   ├── App.jsx      # Main component
│   │   └── App.css      # Styling
│   └── package.json
└── README.md
```

## Features

- **PDF Processing**: Extracts sections, subsections, and tables from bylaw PDFs
- **AI Translation**: Converts legal text into plain English with structured components
- **Table Support**: Automatically includes table data in translations
- **Web Interface**: Clean, minimal UI with drag-and-drop file upload
- **Production Ready**: Structured codebase with separation of concerns

## How to Run Locally

### Prerequisites

- Python 3.11+
- Node.js 18+
- OpenAI API key

### Backend Setup

1. Navigate to backend directory:
   ```bash
   cd backend
   ```

2. Create virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create `.env` file:
   ```
   OPENAI_API_KEY=your-openai-api-key-here
   ```

5. Run the server:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

Backend will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Run development server:
   ```bash
   npm run dev
   ```

Frontend will be available at `http://localhost:3000`

### First Run Note

On first run, Docling will download ML models (~400MB). This takes 2-5 minutes and only happens once. Subsequent runs are faster.

## Approach & Architecture

### Step 1: PDF Extraction

**Technology**: Docling (IBM's document processing library)

**Why Docling?**
- Advanced table extraction with structure preservation
- Handles complex layouts and nested sections
- Better than basic PDF libraries for legal documents
- Automatically detects sections, headers, and tables

**Process**:
1. Docling converts PDF to structured JSON
2. Custom parser walks the document tree
3. Detects numeric sections (e.g., "2.2.1") and lettered clauses (e.g., "(a)", "(i)")
4. Groups tables with their parent sections
5. Outputs structured JSON with sections, parent relationships, and tables

### Step 2: Semantic Translation

**Technology**: OpenAI GPT-4o-mini

**Why OpenAI?**
- High-quality semantic understanding
- Consistent JSON output with structured prompts
- Handles complex legal language translation
- Cost-effective for production use

**Process**:
1. Filters sections with body text or tables
2. For each section, sends to OpenAI with:
   - Section ID, title, and full text
   - Formatted table data (if present)
   - Structured prompt requesting specific fields
3. Extracts: description, condition_english, requirement_english, exception
4. Outputs translated JSON

### Architecture Decisions

**Backend (FastAPI)**:
- **Routes**: Separate files for extraction and translation endpoints
- **Services**: Business logic isolated from API layer
- **Prompts**: Centralized prompt templates for easy updates
- **Utils**: Reusable helper functions

**Frontend (React + Vite)**:
- **Minimal UI**: Focus on core functionality
- **Dark Theme**: Modern, professional appearance
- **Drag & Drop**: Enhanced UX for file upload
- **Loading States**: Clear feedback during processing

**Why This Stack?**
- FastAPI: Fast, async, automatic API docs, production-ready
- React + Vite: Modern, fast development, great DX
- Docling: Best-in-class document processing
- OpenAI: Reliable, high-quality translations

## API Endpoints

### Main Endpoint

**POST** `/api/process`
- Upload PDF file
- Automatically extracts and translates
- Returns job_id and download URLs

**Response**:
```json
{
  "job_id": "uuid",
  "status": "success",
  "sections_count": 50,
  "translated_count": 45,
  "download_urls": {
    "extracted": "/api/download/extracted/{job_id}",
    "translated": "/api/download/translated/{job_id}"
  }
}
```

### Download Endpoints

**GET** `/api/download/extracted/{job_id}`
- Download extracted sections JSON

**GET** `/api/download/translated/{job_id}`
- Download translated sections JSON

## How to Use the Deployed App

1. **Access the Application**
   - Open the deployed frontend URL in your browser

2. **Upload PDF**
   - Drag and drop a PDF file or click to choose
   - Only PDF files are accepted

3. **Process**
   - Click "Process PDF" button
   - Wait for processing (1-2 minutes)
   - Loading messages will cycle showing progress

4. **Download Results**
   - After processing, two download buttons appear:
     - **Download Extracted Sections**: Raw structured sections from PDF
     - **Download Translated Sections**: AI-translated plain English versions

5. **Upload Another File**
   - Click "Upload Another File" to process more PDFs

## Output Format

### Extracted Sections (`sections.json`)
```json
{
  "sections": [
    {
      "parent_section": "2.2",
      "section": "2.2.1",
      "section_title": null,
      "section_body_text": "A new multiple dwelling...",
      "section_start_page": 4,
      "section_end_page": 4,
      "tables": []
    }
  ]
}
```

### Translated Sections (`translated_sections.json`)
```json
{
  "translated_sections": [
    {
      "id": "2.2.1",
      "description": "New multiple dwellings must meet tree retention requirements...",
      "condition_english": "Applies to new multiple dwelling, duplex with secondary suite...",
      "requirement_english": "Sites under 15.1m wide must retain or plant at least one front-yard tree...",
      "exception": {
        "condition_english": "Site has no lane access.",
        "requirement_english": "Director of Planning may waive the tree requirement."
      }
    }
  ]
}
```

## Limitations

- **PDF Format**: Optimized for structured legal documents (bylaws, regulations)
- **Processing Time**: Large PDFs may take 2-5 minutes
- **Model Download**: First run requires downloading Docling models (~400MB)
- **API Costs**: Translation uses OpenAI API (costs apply)
- used to parse the given pdf only

## Troubleshooting

### Docling Model Errors

If you see "Missing ONNX file" errors:

1. Delete the corrupted cache:
   ```bash
   # Windows PowerShell
   Remove-Item -Recurse -Force "$env:USERPROFILE\.cache\huggingface\hub\models--ds4sd--docling-models"
   ```

2. Restart the server - models will re-download automatically

### API Key Issues

Ensure `.env` file exists in `backend/` directory with:
```
OPENAI_API_KEY=your-key-here
```

## Development

### Backend
- Code follows separation of concerns
- Services are testable and modular
- Easy to extend with new extraction/translation methods

### Frontend
- Component-based React architecture
- Minimal dependencies
- Responsive design


