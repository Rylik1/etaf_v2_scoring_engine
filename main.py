"""
ETAF v2 Microservice for Railway Deployment
Threat Assessment Framework v2 with Spark NLP

Test locally:
curl -X POST http://localhost:8000/score -H "Content-Type: application/json" -d @test_payload.json

Test on Railway:
curl -X POST https://your-railway-app.railway.app/score -H "Content-Type: application/json" -d @test_payload.json
"""

import os
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from models.schemas import ScoringRequest, ScoringResponse
from scoring.etaf_logic import score_etaf_v2
from utils.spark_init import initialize_spark_nlp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="ETAF v2 Scoring Service",
    description="Enhanced Threat Assessment Framework v2 for Arabic and Farsi text analysis",
    version="2.0.0"
)

# Add CORS middleware for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variable to store Spark NLP pipeline
spark_pipeline = None

@app.on_event("startup")
async def startup_event():
    """Initialize Spark NLP on application startup"""
    global spark_pipeline
    try:
        logger.info("Initializing Spark NLP pipeline...")
        spark_pipeline = initialize_spark_nlp()
        logger.info("Spark NLP pipeline initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Spark NLP: {str(e)}")
        raise e

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "ETAF v2 Scoring Service",
        "status": "operational",
        "version": "2.0.0",
        "spark_nlp_ready": spark_pipeline is not None
    }

@app.get("/health")
async def health_check():
    """Detailed health check for Railway monitoring"""
    return {
        "status": "healthy",
        "spark_nlp_initialized": spark_pipeline is not None,
        "supported_languages": ["ar", "fa"],
        "components": ["temporal", "operational", "specificity", "source_intent"]
    }

@app.post("/score", response_model=ScoringResponse)
async def score_message(request: ScoringRequest):
    """
    Score a message using ETAF v2 framework
    
    Args:
        request: ScoringRequest containing message text, language, and metadata
        
    Returns:
        ScoringResponse with ETAF score, level, components, and rationale
    """
    try:
        logger.info(f"Scoring request received: lang={request.lang}, text_length={len(request.message_text)}")
        
        # Validate Spark NLP is ready
        if spark_pipeline is None:
            raise HTTPException(
                status_code=503, 
                detail="Spark NLP pipeline not initialized"
            )
        
        # Validate language support
        if request.lang not in ["ar", "fa"]:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported language: {request.lang}. Supported: ar, fa"
            )
        
        # Set global pipeline for scoring function
        import scoring.etaf_logic
        scoring.etaf_logic.spark_pipeline = spark_pipeline
        
        # Perform ETAF v2 scoring
        scoring_result = score_etaf_v2(
            text=request.message_text,
            lang=request.lang,
            metadata=request.channel_metadata
        )
        
        logger.info(f"Scoring completed: score={scoring_result['etaf_score']}, level={scoring_result['level']}")
        
        return ScoringResponse(**scoring_result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Scoring error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal scoring error: {str(e)}"
        )

if __name__ == "__main__":
    # Get port from environment (Railway sets PORT automatically)
    port = int(os.getenv("PORT", 8000))
    
    # Run the application
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        log_level="info",
        reload=False  # Set to True for development
    )