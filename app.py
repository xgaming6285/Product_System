import os
import json
import tempfile
from typing import List, Optional

import uvicorn
from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Import document processing modules
from document_processor import process_documents, get_vector_store
# Import Agent modules
from agent import create_products_agent

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="Products Agent")

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create data directories if they don't exist
os.makedirs("./data", exist_ok=True)
os.makedirs("./data/vectordb", exist_ok=True)
os.makedirs("./static", exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def get_home():
    """Serve the home page"""
    with open('static/index.html', 'r') as f:
        return f.read()

@app.post("/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    """Upload and process documents to add to the vector store"""
    try:
        # Save uploaded files temporarily
        temp_file_paths = []
        for file in files:
            content = await file.read()
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
                temp_file.write(content)
                temp_file_paths.append(temp_file.name)
        
        # Process documents
        document_count = process_documents(temp_file_paths)
        
        # Clean up temp files
        for path in temp_file_paths:
            os.unlink(path)
        
        return JSONResponse(content={
            "status": "success",
            "message": f"Successfully processed {document_count} documents"
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat(question: str = Form(...)):
    """Send a question to the Products Agent"""
    try:
        vector_store = get_vector_store()
        agent = create_products_agent(vector_store)
        
        # Get response from the agent
        response = agent.invoke({"input": question})
        
        return JSONResponse(content={
            "status": "success",
            "response": response["output"]
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True) 