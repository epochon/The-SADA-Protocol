from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.agent.analysis import StockAnalysisAgent
from app.agent.report_generator import ReportGenerator

router = APIRouter()

@router.get("/download/{symbol}")
def download_excel_report(symbol: str, exchange: str = "NSE", format: str = "excel"):
    """
    Generate and download a comprehensive financial report.
    supported formats: excel, csv, text
    """
    try:
        agent = StockAnalysisAgent()
        data = agent.analyze_stock(symbol, exchange)
        
        if not data:
            return {"error": "Could not fetch data"}

        reporter = ReportGenerator(data)
        
        if format == "csv":
            zip_io = reporter.generate_csv_zip()
            return StreamingResponse(
                zip_io,
                media_type="application/zip",
                headers={"Content-Disposition": f"attachment; filename={symbol}_{exchange}_Report.zip"}
            )
        elif format == "text":
            text_io = reporter.generate_text_report()
            return StreamingResponse(
                text_io,
                 media_type="text/plain",
                headers={"Content-Disposition": f"attachment; filename={symbol}_{exchange}_Report.txt"}
            )
        else:
            # Default to Excel
            excel_io = reporter.generate_excel_report()
            return StreamingResponse(
                excel_io,
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={"Content-Disposition": f"attachment; filename={symbol}_{exchange}_Report.xlsx"}
            )

    except Exception as e:
        return {"error": str(e)}
