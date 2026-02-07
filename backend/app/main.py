from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import market, agent, report, hypeslayer
from app.middleware import AdversarialDefenseMiddleware

app = FastAPI(
    title="DAS AI - HypeSlayer Financial Reality Check Agent",
    description="Financial Reality Check Agent Backend - Analyzes financial content for hype and verifies claims against real market data.",
    version="1.0.0"
)

# Configure CORS for Frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "*"],  # Allow all origins for hackathon demo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add Adversarial Defense Middleware
app.add_middleware(AdversarialDefenseMiddleware)

# ==================== Existing Routes ====================
# Market Data Routes (yfinance-powered)
app.include_router(market.router, prefix="/market", tags=["Market Data"])

# AI Advisor Agent Routes (OpenAI function calling)
app.include_router(agent.router, prefix="/agent", tags=["AI Advisor"])

# Report Generation Routes
app.include_router(report.router, prefix="/report", tags=["Reports"])

# ==================== HypeSlayer Routes ====================
# Using consistent prefix for all HypeSlayer operations
app.include_router(hypeslayer.router, prefix="/hypeslayer", tags=["HypeSlayer"])


@app.get("/")
def read_root():
    return {
        "status": "active",
        "agent": "DAS AI - HypeSlayer",
        "description": "Financial Reality Check Agent",
        "endpoints": {
            "hype_slayer": "/api",
            "market": "/market",
            "agent": "/agent",
            "report": "/report"
        }
    }


@app.get("/health")
def health_check():
    """Basic health check for the main app."""
    return {"status": "healthy", "agent": "DAS AI HypeSlayer"}
