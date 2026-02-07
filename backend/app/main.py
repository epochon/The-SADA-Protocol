from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="The SADA Protocol (DAAS)", description="Financial Advisor Agent Backend")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "active", "agent": "The SADA Protocol"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
