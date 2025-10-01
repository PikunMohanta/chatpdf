from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Form
from fastapi.responses import JSONResponse, FileResponse
from typing import List, Optional
import os
import tempfile
import shutil
import logging
from pydantic import BaseModel
import uuid
from datetime import datetime
from pathlib import Path
import fitz  # PyMuPDF
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Optional imports for production use
try:
    import boto3
    from botocore.exceptions import ClientError
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("boto3 not available - S3 features disabled for local development")

try:
    from langchain_openai import OpenAIEmbeddings
    LANGCHAIN_OPENAI_AVAILABLE = True
except ImportError:
    LANGCHAIN_OPENAI_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("langchain_openai not available - using mock embeddings for local development")

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("chromadb not available - using mock storage for local development")

from .auth import verify_token, UserInfo

router = APIRouter()
logger = logging.getLogger(__name__)

# Pydantic models
class UploadResponse(BaseModel):
    document_id: str
    filename: str
    status: str
    page_count: int
    text_length: int

class DocumentInfo(BaseModel):
    document_id: str
    filename: str
    upload_date: datetime
    page_count: int
    status: str

# AWS S3 configuration
S3_BUCKET = os.getenv("S3_BUCKET_NAME", "newchat-documents")

# Initialize S3 client only if AWS credentials are available
try:
    # Check if AWS credentials are configured
    aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    
    if aws_access_key and aws_secret_key:
        s3_client = boto3.client('s3')
        # Test the credentials with a simple operation
        s3_client.list_buckets()
        S3_ENABLED = True
        logger.info("S3 client initialized successfully")
    else:
        raise Exception("AWS credentials not configured")
except Exception as e:
    s3_client = None
    S3_ENABLED = False
    logger.warning(f"S3 client not available - using local storage for development: {e}")

# Initialize OpenAI embeddings - check OpenRouter key first, fallback to OpenAI
if LANGCHAIN_OPENAI_AVAILABLE:
    try:
        openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        openai_api_key = os.getenv("OPENAI_API_KEY")
        
        if openrouter_api_key:
            # Use OpenRouter for embeddings (they proxy OpenAI's embedding models)
            embeddings = OpenAIEmbeddings(
                openai_api_key=openrouter_api_key,
                base_url="https://openrouter.ai/api/v1",
                model="text-embedding-ada-002"
            )
            EMBEDDINGS_ENABLED = True
            logger.info("OpenAI embeddings initialized with OpenRouter")
        elif openai_api_key:
            # Fallback to direct OpenAI API
            embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
            EMBEDDINGS_ENABLED = True
            logger.info("OpenAI embeddings initialized")
        else:
            embeddings = None
            EMBEDDINGS_ENABLED = False
            logger.warning("No API keys found - using mock embeddings")
    except Exception as e:
        embeddings = None
        EMBEDDINGS_ENABLED = False
        logger.warning(f"OpenAI embeddings not available - using mock mode for development: {e}")
else:
    embeddings = None
    EMBEDDINGS_ENABLED = False
    logger.warning("langchain_openai not available - using mock embeddings for local development")

# Initialize ChromaDB client only if available
if CHROMADB_AVAILABLE:
    try:
        chroma_client = chromadb.PersistentClient(path="./data/chromadb")
        CHROMADB_ENABLED = True
        logger.info("ChromaDB initialized successfully")
    except Exception as e:
        chroma_client = None
        CHROMADB_ENABLED = False
        logger.warning(f"ChromaDB initialization failed: {e}")
else:
    chroma_client = None
    CHROMADB_ENABLED = False
    logger.warning("ChromaDB not available - using mock storage for development")

# Text splitter for chunking
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    length_function=len,
)

def extract_text_from_pdf(pdf_path: str) -> tuple[str, int]:
    """
    Extract text from PDF using PyMuPDF
    Returns: (extracted_text, page_count)
    """
    try:
        doc = fitz.open(pdf_path)
        text_content = ""
        page_count = len(doc)
        
        for page_num in range(page_count):
            page = doc[page_num]
            text_content += page.get_text()
            text_content += "\n\n"  # Add page breaks
        
        doc.close()
        return text_content, page_count
        
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {e}")
        raise HTTPException(status_code=500, detail="Failed to extract text from PDF")

def upload_to_s3(file_path: str, s3_key: str) -> str:
    """
    Upload file to S3 and return the S3 URL
    For local development, save to local storage
    """
    if not S3_ENABLED:
        # For local development - save to local storage
        local_storage_dir = Path("./data/uploads")
        local_storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Create the local file path
        local_file_path = local_storage_dir / s3_key.replace("/", "_")
        
        # Copy the file to local storage
        import shutil
        shutil.copy2(file_path, local_file_path)
        
        logger.info(f"File saved locally: {local_file_path}")
        return f"local://{local_file_path}"
    
    try:
        s3_client.upload_file(file_path, S3_BUCKET, s3_key)
        
        # Generate a presigned URL for access (valid for 1 hour)
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': S3_BUCKET, 'Key': s3_key},
            ExpiresIn=3600
        )
        return url
        
    except ClientError as e:
        logger.error(f"Error uploading to S3: {e}")
        raise HTTPException(status_code=500, detail="Failed to upload file to storage")

def create_embeddings(text: str, document_id: str) -> str:
    """
    Create embeddings from text and save to local storage
    For local development, uses mock storage when dependencies are unavailable
    Returns: path to saved collection
    """
    try:
        # Split text into chunks
        chunks = text_splitter.split_text(text)
        
        if not CHROMADB_ENABLED or not EMBEDDINGS_ENABLED:
            # Mock mode for local development
            logger.info(f"Mock embeddings creation for document {document_id} with {len(chunks)} chunks")
            # Create local directory for mock storage
            import os
            mock_dir = f"./data/mock_embeddings"
            os.makedirs(mock_dir, exist_ok=True)
            
            # Save chunks to a simple JSON file for mock retrieval
            import json
            mock_data = {
                "document_id": document_id,
                "chunks": chunks,
                "created_at": str(datetime.now())
            }
            
            mock_file = f"{mock_dir}/doc_{document_id}.json"
            with open(mock_file, 'w', encoding='utf-8') as f:
                json.dump(mock_data, f, ensure_ascii=False, indent=2)
            
            return mock_file
        
        # Real ChromaDB implementation
        collection_name = f"doc_{document_id}"
        collection = chroma_client.get_or_create_collection(
            name=collection_name,
            metadata={"document_id": document_id}
        )
        
        # Generate embeddings for chunks
        chunk_embeddings = embeddings.embed_documents(chunks)
        
        # Add documents to collection
        collection.add(
            documents=chunks,
            embeddings=chunk_embeddings,
            ids=[f"{document_id}_{i}" for i in range(len(chunks))]
        )
        
        # Return collection path info
        collection_path = f"./data/chromadb/{collection_name}"
        
        return collection_path
        
    except Exception as e:
        logger.error(f"Error creating embeddings: {e}")
        raise HTTPException(status_code=500, detail="Failed to create document embeddings")

@router.post("/upload", response_model=UploadResponse)
async def upload_pdf(
    file: UploadFile = File(...),
    current_user: UserInfo = Depends(verify_token)
):
    """
    Upload and process PDF file
    """
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    document_id = str(uuid.uuid4())
    
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            # Save uploaded file
            shutil.copyfileobj(file.file, temp_file)
            temp_path = temp_file.name
        
        # Extract text from PDF
        text_content, page_count = extract_text_from_pdf(temp_path)
        
        # Upload to S3
        s3_key = f"documents/{current_user.user_id}/{document_id}.pdf"
        s3_url = upload_to_s3(temp_path, s3_key)
        
        # Create embeddings
        index_path = create_embeddings(text_content, document_id)
        
        # TODO: Save document metadata to PostgreSQL
        # - document_id, filename, user_id, s3_key, index_path, page_count, upload_date
        
        # Clean up temporary file
        os.unlink(temp_path)
        
        logger.info(f"Successfully processed PDF: {file.filename} for user: {current_user.user_id}")
        
        return UploadResponse(
            document_id=document_id,
            filename=file.filename,
            status="processed",
            page_count=page_count,
            text_length=len(text_content)
        )
        
    except Exception as e:
        # Clean up on error
        if 'temp_path' in locals():
            try:
                os.unlink(temp_path)
            except:
                pass
        
        logger.error(f"Error processing PDF upload: {e}")
        raise HTTPException(status_code=500, detail="Failed to process PDF file")

@router.get("/documents", response_model=List[DocumentInfo])
async def list_documents(current_user: UserInfo = Depends(verify_token)):
    """
    List all documents for the current user
    """
    # TODO: Implement database query to get user's documents
    # For now, return mock data
    return [
        DocumentInfo(
            document_id="sample-doc-1",
            filename="sample.pdf",
            upload_date=datetime.now(),
            page_count=10,
            status="processed"
        )
    ]

@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: str,
    current_user: UserInfo = Depends(verify_token)
):
    """
    Delete a document and its associated data
    """
    try:
        # TODO: Implement document deletion
        # 1. Delete from S3
        # 2. Delete embeddings from local storage
        # 3. Delete metadata from database
        
        return {"message": f"Document {document_id} deleted successfully"}
        
    except Exception as e:
        logger.error(f"Error deleting document {document_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete document")

@router.get("/documents/{document_id}/text")
async def get_document_text(
    document_id: str,
    current_user: UserInfo = Depends(verify_token)
):
    """
    Get extracted text from a document
    """
    # TODO: Implement text retrieval from database or re-extract from S3
    return {"text": "Sample extracted text from document"}

@router.get("/documents/{document_id}/download")
async def download_document(
    document_id: str,
    current_user: UserInfo = Depends(verify_token)
):
    """
    Generate presigned URL for document download or local file path
    """
    try:
        s3_key = f"documents/{current_user.user_id}/{document_id}.pdf"
        
        if not S3_ENABLED:
            # For local development - check if file exists locally
            local_storage_dir = Path("./data/uploads")
            local_file_name = s3_key.replace("/", "_")
            local_file_path = local_storage_dir / local_file_name
            
            if local_file_path.exists():
                # Return a local file URL that the frontend can use
                return {"download_url": f"http://localhost:8000/api/pdf/files/{local_file_name}"}
            else:
                raise HTTPException(status_code=404, detail="Document not found")
        
        # S3 mode - generate presigned URL
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': S3_BUCKET, 'Key': s3_key},
            ExpiresIn=3600  # 1 hour
        )
        
        return {"download_url": url}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating download URL: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate download URL")

@router.get("/document/{document_id}/preview")
async def preview_document(
    document_id: str,
    current_user: UserInfo = Depends(verify_token)
):
    """
    Serve PDF file for preview in browser
    """
    try:
        s3_key = f"documents/{current_user.user_id}/{document_id}.pdf"
        
        if not S3_ENABLED:
            # For local development - serve file directly
            local_storage_dir = Path("./data/uploads")
            local_file_name = s3_key.replace("/", "_")
            local_file_path = local_storage_dir / local_file_name
            
            if not local_file_path.exists():
                raise HTTPException(status_code=404, detail="Document not found")
            
            return FileResponse(
                path=str(local_file_path),
                media_type='application/pdf',
                filename=f"{document_id}.pdf"
            )
        
        # S3 mode - redirect to presigned URL
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': S3_BUCKET, 'Key': s3_key},
            ExpiresIn=3600  # 1 hour
        )
        
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url=url)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error previewing document {document_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to load document preview")

@router.get("/files/{filename}")
async def serve_local_file(
    filename: str,
    current_user: UserInfo = Depends(verify_token)
):
    """
    Serve locally stored PDF files for development
    """
    try:
        local_storage_dir = Path("./data/uploads")
        file_path = local_storage_dir / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        return FileResponse(
            path=str(file_path),
            media_type='application/pdf',
            filename=filename
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error serving file {filename}: {e}")
        raise HTTPException(status_code=500, detail="Failed to serve file")