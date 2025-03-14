import os
import pytesseract
from typing import List, Optional
from pathlib import Path
from dotenv import load_dotenv

from PIL import Image
from pypdf import PdfReader

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

# Load environment variables
load_dotenv()

# Vector DB path
VECTOR_DB_DIR = os.getenv("VECTOR_DB_DIR", "./data/vectordb")

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from a PDF file"""
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

def extract_text_from_image(image_path: str) -> str:
    """Extract text from an image using OCR"""
    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        print(f"Error extracting text from image: {e}")
        return ""

def process_documents(file_paths: List[str]) -> int:
    """Process documents and add to vector store"""
    documents = []
    
    # Extract text from documents
    for file_path in file_paths:
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext in ('.pdf'):
            text = extract_text_from_pdf(file_path)
            source = Path(file_path).name
            documents.append(Document(page_content=text, metadata={"source": source}))
            
        elif file_ext in ('.png', '.jpg', '.jpeg'):
            text = extract_text_from_image(file_path)
            source = Path(file_path).name
            documents.append(Document(page_content=text, metadata={"source": source}))
    
    if not documents:
        return 0
    
    # Split documents
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
        length_function=len,
    )
    chunks = text_splitter.split_documents(documents)
    
    # Store in vector DB
    embeddings = OpenAIEmbeddings()
    
    # Check if vector store exists, create or add to it
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=VECTOR_DB_DIR
    )
    
    # Persist the vector store
    vector_store.persist()
    
    return len(documents)

def get_vector_store():
    """Get the vector store"""
    embeddings = OpenAIEmbeddings()
    
    # Initialize Chroma from the persisted directory
    vector_store = Chroma(
        persist_directory=VECTOR_DB_DIR,
        embedding_function=embeddings
    )
    
    return vector_store 