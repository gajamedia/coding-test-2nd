from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from models.schemas import ChatRequest, UploadResponse, ChatResponse, DocumentsResponse
from services.pdf_processor import PDFProcessor
from services.vector_store import VectorStoreService
from services.rag_pipeline import RAGPipeline
from config import settings
from pydantic import BaseModel
import logging
import uuid
import os

# Logging
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="RAG-based Financial Statement Q&A System",
    description="AI-powered Q&A system for financial documents using RAG",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global services
pdf_processor: PDFProcessor = None
# vector_store: VectorStoreService = None
# rag_pipeline: RAGPipeline = None
# Inisialisasi pipeline
vector_store = VectorStoreService()
rag_pipeline = RAGPipeline(vector_store)

class AskRequest(BaseModel):
    question: str
    history: list[dict[str, str]] = []

# STORAGE PATH
UPLOAD_DIR = "./uploaded_pdfs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.on_event("startup")
async def startup_event():
    global pdf_processor, vector_store, rag_pipeline
    logger.info("Starting RAG Q&A System...")

    pdf_processor = PDFProcessor()
    vector_store = VectorStoreService()
    rag_pipeline = RAGPipeline(vector_store=vector_store)


@app.get("/")
async def root():
    return {"message": "RAG-based Financial Statement Q&A System is running"}


@app.post("/api/upload", response_model=UploadResponse)
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="File must be a PDF")

    try:
        file_id = str(uuid.uuid4())
        save_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file.filename}")
        
        with open(save_path, "wb") as f:
            f.write(await file.read())

        # Extract text and chunk
        chunks = pdf_processor.process(save_path)

        # Store to vector DB
        vector_store.add_document(file_id=file_id, filename=file.filename, chunks=chunks)

        return UploadResponse(
            file_id=file_id,
            filename=file.filename,
            total_chunks=len(chunks),
            status="success"
        )
    except Exception as e:
        logger.exception("Failed to process PDF")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        # answer, sources = rag_pipeline.answer_question(request.question)
        # return ChatResponse(answer=answer, sources=sources)
        result = rag_pipeline.generate_answer(request.question, request.chat_history)
        return result
    except Exception as e:
        logger.exception("Error in chat processing")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/documents", response_model=DocumentsResponse)
async def get_documents():
    try:
        documents = vector_store.get_documents()
        return DocumentsResponse(documents=documents)
    except Exception as e:
        logger.exception("Failed to retrieve documents")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/chunks")
async def get_chunks():
    try:
        return vector_store.get_all_chunks()
    except Exception as e:
        logger.exception("Failed to retrieve chunks")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.host, port=settings.port, reload=settings.debug)
