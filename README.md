# Grounded RAG Chatbot

This project is a document-based Q&A chatbot built with FastAPI, React + Vite, and LangChain. It accepts uploaded PDF or TXT files, splits them into chunks, stores the chunks in a local Chroma vector database, and answers only using the retrieved document evidence.

The system is intentionally grounded: if the answer is not explicitly present in the uploaded files, the app refuses to guess and returns the exact refusal message:

> I cannot find this information in the uploaded document.

This project is designed for document-grounded QA, not for general-purpose web search or open-ended knowledge answers.

## Features

- Upload one or more PDF/TXT files
- Validate file type and size
- Extract text from PDFs and TXT files
- Split content into chunks with overlap
- Store chunks in a local vector database
- Retrieve most relevant chunks for a question
- Generate grounded answers using the retrieved context
- Return source file/page metadata with the response
- Enforce strict answer guardrails to prevent hallucinations
- Support both OpenAI and OpenRouter API keys
- Simple React frontend for chat interaction

## Technology stack

Backend
- Python 3.10+
- FastAPI
- LangChain
- LangChain OpenAI
- Chroma
- pypdf
- Pydantic
- Python-dotenv

Frontend
- React
- Vite
- Tailwind CSS

## Project structure

```text
rag-chatbot/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── main.py
│   │   ├── schemas.py
│   │   └── services/
│   │       ├── document.py
│   │       └── rag.py
│   ├── .env
│   ├── .env.example
│   ├── requirements.txt
│   ├── storage/
│   │   └── chroma/
│   ├── test_api.py
│   ├── test_documents.py
│   └── test_guardrail.py
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── postcss.config.js
│   ├── tailwind.config.js
│   ├── vite.config.js
│   ├── dist/
│   └── src/
│       ├── App.jsx
│       ├── index.css
│       ├── main.jsx
│       └── components/
│           ├── ChatWindow.jsx
│           ├── FileUpload.jsx
│           └── SourceBadge.jsx
├── README.md
└── .github/
    └── copilot-instructions.md
```

## Backend architecture

### 1. Configuration
The backend settings are defined in [backend/app/config.py](backend/app/config.py). They include:

- API key configuration
- model names
- chunk size and overlap
- top-k retrieval count
- upload size and file count limits
- CORS origins
- vector database path

### 2. Document ingestion
The document processing logic lives in [backend/app/services/document.py](backend/app/services/document.py).

It does the following:

- Accepts uploaded file bytes
- Detects whether the file is PDF or TXT
- Extracts text from the file
- Builds document objects with metadata such as source filename and page number
- Splits the content using a recursive character splitter
- Adds chunk_index metadata to each chunk

### 3. Retrieval and answering
The main RAG logic is in [backend/app/services/rag.py](backend/app/services/rag.py).

It:

- Initializes embeddings
- Builds or restores a Chroma vectorstore
- Retrieves the top N similar chunks for a question
- Builds a grounded prompt using the retrieved context
- Calls the configured LLM
- Returns the final answer and source metadata

### 4. API layer
The API is defined in [backend/app/main.py](backend/app/main.py).

Endpoints:

- GET /health
  - Health check endpoint
- POST /upload
  - Upload one or more PDF/TXT files
  - Validate file size and type
  - Build the vector store for the uploaded content
- POST /ask
  - Ask a grounded question about the uploaded document
  - Returns answer and evidence sources

## Frontend architecture

The UI is built with React and Vite in [frontend/src/App.jsx](frontend/src/App.jsx).

Main responsibilities:

- Upload documents
- Send chat questions to the backend
- Render chat messages
- Show retrieved source snippets
- Handle upload/loading states

Key components:

- [frontend/src/components/FileUpload.jsx](frontend/src/components/FileUpload.jsx)
  - File selection and drag-and-drop upload UI
- [frontend/src/components/ChatWindow.jsx](frontend/src/components/ChatWindow.jsx)
  - Chat messages, input handling, and voice support
- [frontend/src/components/SourceBadge.jsx](frontend/src/components/SourceBadge.jsx)
  - Displays source info for the current answer

## Environment configuration

Create a `.env` file inside the `backend` folder based on [backend/.env.example](backend/.env.example).

Example:

```env
OPENAI_API_KEY=
OPENROUTER_API_KEY=your_openrouter_key_here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENAI_MODEL=openai/gpt-4o-mini
EMBEDDING_MODEL=openai/text-embedding-3-small
CHUNK_SIZE=1200
CHUNK_OVERLAP=200
TOP_K_RESULTS=4
VECTOR_DB_PATH=./storage/chroma
```

Notes:

- You can use either OpenAI or OpenRouter.
- If OpenAI key is empty, the app prefers OpenRouter automatically.
- A valid key is required for document indexing and answer generation.

## Setup steps

### 1. Backend setup

From the `backend` directory:

```bash
python -m venv .venv
```

Activate the environment:

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Windows Command Prompt:

```cmd
.venv\Scripts\activate.bat
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create your `.env` file and add your key:

```bash
copy .env.example .env
```

### 2. Start the backend

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Health check:

```bash
http://localhost:8000/health
```

### 3. Frontend setup

From the `frontend` directory:

```bash
npm install
npm run dev
```

Then open:

```bash
http://localhost:5173
```

## How to use the app

1. Open the frontend in the browser.
2. Upload one or more PDF/TXT files.
3. Wait until indexing completes.
4. Ask a question in the chat box.
5. The app answers using only the uploaded document content.
6. If no relevant answer is found, it returns:

```text
I cannot find this information in the uploaded document.
```

## Supported file types

- PDF (.pdf)
- TXT (.txt)

## RAG behavior and guardrails

The application follows a strict grounded-RAG flow:

1. Upload document(s)
2. Convert text to chunks
3. Save chunks in vector storage
4. Retrieve only relevant chunks for the question
5. Insert the retrieved context into the LLM prompt
6. Require the answer to be grounded in that context only
7. Refuse to answer when the information is missing or not explicitly stated

This reduces hallucinations and ensures answers remain document-based.

## Validation and testing

The backend includes tests covering:

- upload validation
- missing API key handling
- PDF corruption handling
- document extraction
- grounded refusal behavior
- vectorstore reindexing behavior

Run tests:

```bash
cd backend
python -m pytest -q
```

## Current status

This project is working as a document-grounded chatbot with:

- local vector storage
- PDF/TXT upload support
- grounding guardrails
- OpenAI and OpenRouter compatibility
- frontend chat interface

## Notes

- The app stores files in the local Chroma database path configured in `.env`.
- It keeps the answer scope limited to uploaded documents only.
- It does not include user accounts, multi-user authentication, or a todo-management backend.
- For production deployments, you should add proper authentication, environment security, and persistent storage.
