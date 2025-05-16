"""
Main FastAPI application for Jarvis.
"""

import asyncio
import logging
from typing import Optional
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from core.brain import JarvisBrain

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Jarvis AI Assistant")

# Initialize Jarvis brain
brain = None

class InputRequest(BaseModel):
    text: str

class DocumentRequest(BaseModel):
    path: str

@app.on_event("startup")
async def startup_event():
    """Initialize the Jarvis brain on startup."""
    global brain
    try:
        brain = JarvisBrain()
        await brain.start()
        logger.info("Jarvis brain initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Jarvis brain: {str(e)}")
        raise

@app.post("/process")
async def process_input(request: InputRequest):
    """Process user input and return a response."""
    if not brain:
        raise HTTPException(status_code=500, detail="Jarvis brain not initialized")
    
    try:
        response = await brain.process_input(request.text)
        return {"response": response}
    except Exception as e:
        logger.error(f"Error processing input: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/learn")
async def learn_from_document(request: DocumentRequest):
    """Process and learn from a new document."""
    if not brain:
        raise HTTPException(status_code=500, detail="Jarvis brain not initialized")
    
    try:
        await brain.learn_from_document(request.path)
        return {"status": "success", "message": f"Successfully learned from {request.path}"}
    except Exception as e:
        logger.error(f"Error learning from document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/memory")
async def get_memory_summary():
    """Get a summary of the current memory state."""
    if not brain:
        raise HTTPException(status_code=500, detail="Jarvis brain not initialized")
    
    try:
        summary = brain.get_memory_summary()
        return summary
    except Exception as e:
        logger.error(f"Error getting memory summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def start_server():
    """Start the FastAPI server."""
    config = uvicorn.Config(
        "core.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
    server = uvicorn.Server(config)
    await server.serve()

def main():
    """Main entry point for the Jarvis core system."""
    asyncio.run(start_server())

if __name__ == "__main__":
    main() 