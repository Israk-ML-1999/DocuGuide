import logging
from fastapi import APIRouter, HTTPException

from com.mhire.app.services.contract_analyzer.contract_analyzer import ContractAnalyzer
from com.mhire.app.services.contract_analyzer.contract_analyzer_schema import (
    AnalyzeRequest, AnalyzeResponse, SummarizeRequest, SummarizeResponse
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1",
    tags=["Contract Analyzer"]
)

analyzer = ContractAnalyzer()

@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_contract(request: AnalyzeRequest):
    """
    Analyze contract text and return comprehensive analysis including:
    - Document type classification
    - Key sections with dates, values, payment types (nulls if not found)
    - Red flags and concerns
    - Suggested questions to ask
    - Alternative wording suggestions
    
    All dates are normalized to YYYY-MM-DD format
    """
    try:
        if not request.contract_text or len(request.contract_text.strip()) < 50:
            raise HTTPException(status_code=400, detail="Contract text is too short or empty")
        
        analysis_data = await analyzer.analyze_contract(request.contract_text)
        return AnalyzeResponse(**analysis_data)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in analyze endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/summarize", response_model=SummarizeResponse)
async def summarize_text(request: SummarizeRequest):
    """
    Summarize any text into a concise summary.
    Returns a 3-5 sentence summary capturing the main points.
    """
    try:
        if not request.text or len(request.text.strip()) < 10:
            raise HTTPException(status_code=400, detail="Text is too short or empty")
        
        summary = await analyzer.summarize_text(request.text)
        return SummarizeResponse(summary=summary)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in summarize endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))