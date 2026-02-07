from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import market, agent, report

app = FastAPI(title="The SADA Protocol (DAAS)", description="Financial Advisor Agent Backend")

# Configure CORS for Frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Market Routes
app.include_router(market.router, prefix="/market", tags=["Market Data"])
app.include_router(agent.router, prefix="/agent", tags=["AI Advisor"])
app.include_router(report.router, prefix="/report", tags=["Reports"])

@app.get("/")
def read_root():
    return {"status": "active", "agent": "The SADA Protocol"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
