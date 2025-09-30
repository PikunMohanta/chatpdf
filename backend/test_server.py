from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Minimal test server
app = FastAPI(title="Minimal Test Server")

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    text: str
    document_id: str

class ChatResponse(BaseModel):
    response: str
    session_id: str
    message_id: str

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Test server is running"}

@app.post("/api/chat/query", response_model=ChatResponse)
def chat_query(request: ChatRequest):
    print(f"Received chat request: {request.text}")
    return ChatResponse(
        response=f"Test response to: {request.text}",
        session_id="test-session",
        message_id="test-message-123"
    )

if __name__ == "__main__":
    print("Starting minimal test server...")
    uvicorn.run(app, host="127.0.0.1", port=8000)