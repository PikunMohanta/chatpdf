# Python 3.13.7 Migration Guide

## Overview

This guide explains the changes made to support Python 3.13.7 and the migration from FAISS to ChromaDB.

## Key Changes

### 1. Vector Database Migration

**Before (FAISS):**
- Used `faiss-cpu==1.7.4` for vector embeddings
- FAISS doesn't have Python 3.13 wheels yet

**After (ChromaDB):**
- Using `chromadb==0.5.7` for vector embeddings
- Full Python 3.13 compatibility
- Better integration with modern LangChain

### 2. Updated Dependencies

All packages have been updated to their latest Python 3.13 compatible versions:

- `fastapi[all]==0.115.0` (was 0.104.1)
- `uvicorn[standard]==0.30.6` (was 0.24.0)
- `langchain==0.3.1` (was 0.0.350)
- `langchain-openai==0.2.1` (new separate package)
- `openai==1.51.0` (was 1.6.1)
- `pydantic==2.9.2` (was 2.5.2)

### 3. Code Changes

#### PDF Processing (`app/pdf_processing.py`)
```python
# Old FAISS implementation
from langchain.vectorstores import FAISS
vectorstore = FAISS.from_texts(chunks, embeddings)
vectorstore.save_local(index_path)

# New ChromaDB implementation
import chromadb
collection = chroma_client.get_or_create_collection(name=collection_name)
collection.add(documents=chunks, embeddings=chunk_embeddings, ids=chunk_ids)
```

#### Chat System (`app/chat.py`)
```python
# Old FAISS query
vectorstore = FAISS.load_local(index_path, embeddings)
qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=vectorstore.as_retriever())

# New ChromaDB query
collection = chroma_client.get_collection(name=collection_name)
results = collection.query(query_texts=[question], n_results=k)
```

## Migration Steps

### 1. Clean Previous Installation

```bash
# Remove old virtual environment
rm -rf env/  # or .venv/ if using UV

# Remove old FAISS indexes
rm -rf ./data/indexes/
```

### 2. Install Python 3.13.7

Download and install Python 3.13.7 from [python.org](https://python.org).

### 3. Install UV Package Manager

```bash
# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 4. Setup New Environment

```bash
cd backend

# Create new virtual environment
uv venv --python python3.13

# Activate environment
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate  # Windows

# Install updated dependencies
uv pip install -r requirements.txt
```

### 5. Update Data Directory Structure

```bash
# Create ChromaDB directory
mkdir -p ./data/chromadb

# Old FAISS structure (can be removed)
# ./data/indexes/

# New ChromaDB structure
# ./data/chromadb/
```

## Benefits of ChromaDB over FAISS

### 1. **Better Python 3.13 Support**
- Native Python 3.13 wheels available
- No compilation required

### 2. **Easier Management**
- Persistent storage by default
- Better metadata support
- Built-in filtering capabilities

### 3. **Modern Architecture**
- REST API support
- Better scaling options
- Cloud deployment ready

### 4. **Developer Experience**
- Better error messages
- Easier debugging
- More intuitive API

## Performance Comparison

| Aspect | FAISS | ChromaDB |
|--------|-------|----------|
| Setup Time | Fast | Fast |
| Query Speed | Very Fast | Fast |
| Memory Usage | Low | Medium |
| Python 3.13 | ❌ | ✅ |
| Ease of Use | Medium | High |
| Persistence | Manual | Automatic |

## Troubleshooting

### ChromaDB Installation Issues

If you encounter issues installing ChromaDB:

```bash
# Try installing with UV's build isolation
uv pip install --no-build-isolation chromadb

# Or install dependencies separately
uv pip install numpy pandas
uv pip install chromadb
```

### Data Migration

If you have existing FAISS data, you'll need to re-process your PDFs:

1. Upload PDFs again through the UI
2. The new system will automatically create ChromaDB collections
3. Old FAISS indexes can be safely deleted

### Performance Tuning

ChromaDB configuration for better performance:

```python
# In your code, you can tune ChromaDB settings
chroma_client = chromadb.PersistentClient(
    path="./data/chromadb",
    settings=Settings(
        chroma_db_impl="duckdb+parquet",
        persist_directory="./data/chromadb"
    )
)
```

## Rollback Plan

If you need to rollback to FAISS:

1. Downgrade Python to 3.12 or lower
2. Restore the old requirements.txt
3. Restore the old FAISS-based code from git history

## Future Considerations

- FAISS may release Python 3.13 wheels in the future
- ChromaDB provides a more modern foundation for future features
- The current implementation can be easily extended with filters and metadata
- ChromaDB supports both local and cloud deployments

## Testing

Run the test suite to ensure everything works:

```bash
# Backend tests
cd backend
source .venv/bin/activate
pytest tests/

# Integration tests
python scripts/test_integration.py
```

The migration to Python 3.13.7 and ChromaDB provides better compatibility, easier maintenance, and a more modern foundation for future development.