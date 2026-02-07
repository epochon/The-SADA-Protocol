from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.agent.analysis import StockAnalysisAgent
from app.agent.report_generator import ReportGenerator

router = APIRouter()

@router.get("/download/{symbol}")
def download_excel_report(symbol: str, exchange: str = "NSE"):
    """
    Generate and download a comprehensive Excel report.
    """
    try:
        agent = StockAnalysisAgent()
        data = agent.analyze_stock(symbol, exchange)
        
        if not data:
            return {"error": "Could not fetch data"}

        reporter = ReportGenerator(data)
        excel_io = reporter.generate_excel_report()
        
        return StreamingResponse(
            excel_io,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={symbol}_{exchange}_Report.xlsx"}
        )
    except Exception as e:
        return {"error": str(e)}
