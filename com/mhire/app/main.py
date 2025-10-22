from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse

from com.mhire.app.services.contract_analyzer.contract_analyzer_router import router as contract_analyzer_router

app = FastAPI(
    title="Contract Analyzer API",
    description="AI-powered contract analysis application using Claude",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(contract_analyzer_router)

@app.get("/", status_code=status.HTTP_200_OK, response_class=PlainTextResponse)
async def health_check():
    return "Contract Analyzer Server is running"