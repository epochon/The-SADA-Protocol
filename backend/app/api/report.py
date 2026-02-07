from fastapi import APIRouter
from app.agent.analysis import StockAnalysisAgent

router = APIRouter()

@router.get("/analyze/{symbol}")
def analyze_stock(symbol: str, exchange: str = "NSE"):
    """
    Directly analyze a stock and return JSON data (For frontend preview)
    """
    try:
        agent = StockAnalysisAgent()
        data = agent.analyze_stock(symbol, exchange)
        if not data:
            return {"error": "Could not fetch data"}
        return data
    except Exception as e:
        return {"error": str(e)}

# Re-export previous download endpoint
from app.api.report import download_excel_report as download_report_logic

@router.get("/download/{symbol}")
def download_excel_report(symbol: str, exchange: str = "NSE", format: str = "excel"):
    return download_report_logic(symbol, exchange, format)
