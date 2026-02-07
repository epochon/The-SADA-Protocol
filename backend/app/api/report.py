from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.agent.analysis import StockAnalysisAgent
from app.agent.report_generator import ReportGenerator

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

@router.get("/download/{symbol}")
def download_excel_report(symbol: str, exchange: str = "NSE", format: str = "excel"):
    """
    Download a comprehensive stock report in specified format.
    Supported formats: excel, csv, text
    """
    try:
        agent = StockAnalysisAgent()
        data = agent.analyze_stock(symbol, exchange)
        
        if not data or "error" in data:
            return {"error": "Could not fetch data for report generation"}
        
        generator = ReportGenerator(data)
        
        if format == "excel":
            output = generator.generate_excel_report()
            return StreamingResponse(
                output,
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={"Content-Disposition": f"attachment; filename={symbol}_report.xlsx"}
            )
        elif format == "text":
            output = generator.generate_text_report()
            return StreamingResponse(
                output,
                media_type="text/plain",
                headers={"Content-Disposition": f"attachment; filename={symbol}_report.txt"}
            )
        elif format == "csv":
            output = generator.generate_csv_zip()
            return StreamingResponse(
                output,
                media_type="application/zip",
                headers={"Content-Disposition": f"attachment; filename={symbol}_report.zip"}
            )
        else:
            return {"error": f"Unsupported format: {format}"}
            
    except Exception as e:
        return {"error": str(e)}
