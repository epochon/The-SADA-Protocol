"""
Indian Stock Market Analysis AI Agent
Fetches comprehensive financial data and generates detailed reports
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class StockAnalysisAgent:
    """
    AI Agent for comprehensive Indian stock market analysis
    Provides detailed financial reports with all company data
    """
    
    def __init__(self):
        self.report_data = {}
        
    def analyze_stock(self, symbol, exchange="NSE"):
        """
        Main analysis function - gets all available data for a stock
        
        Args:
            symbol: Stock symbol (e.g., 'RELIANCE', 'TCS', 'INFY')
            exchange: 'NSE' or 'BSE' (default: NSE)
            
        Returns:
            dict: Complete stock analysis data
        """
        # Format ticker symbol
        ticker_symbol = f"{symbol}.NS" if exchange == "NSE" else f"{symbol}.BO"
        
        # Initialize yfinance ticker
        stock = yf.Ticker(ticker_symbol)
        
        try:
            # Collect all data
            self.report_data = {
                'symbol': symbol,
                'exchange': exchange,
                'ticker_symbol': ticker_symbol,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'company_profile': self._get_company_profile(stock),
                'current_market_data': self._get_current_market_data(stock),
                'valuation_metrics': self._get_valuation_metrics(stock),
                'financial_health': self._get_financial_health(stock),
                'profitability_metrics': self._get_profitability_metrics(stock),
                'growth_metrics': self._get_growth_metrics(stock),
                'dividend_info': self._get_dividend_info(stock),
                'price_performance': self._get_price_performance(stock),
                # Historical prices and financial statements are heavy, maybe skip for chat summary or limit?
                # 'historical_prices': self._get_historical_prices(stock),
                # 'financial_statements': self._get_financial_statements(stock), 
                # 'quarterly_results': self._get_quarterly_results(stock),
                'analyst_info': self._get_analyst_info(stock),
                'risk_metrics': self._get_risk_metrics(stock)
            }
            
            return self.report_data
            
        except Exception as e:
            print(f"❌ Error analyzing {symbol}: {str(e)}")
            return {"error": str(e)}
    
    def _get_company_profile(self, stock):
        """Get detailed company information"""
        info = stock.info
        return {
            'Company Name': info.get('longName', 'N/A'),
            'Sector': info.get('sector', 'N/A'),
            'Industry': info.get('industry', 'N/A'),
            'Country': info.get('country', 'India'),
            'Business Summary': info.get('longBusinessSummary', 'N/A'),
        }
    
    def _get_current_market_data(self, stock):
        """Get current market price and trading data"""
        info = stock.info
        return {
            'Current Price': info.get('currentPrice', info.get('regularMarketPrice', 'N/A')),
            'Previous Close': info.get('previousClose', 'N/A'),
            '52 Week High': info.get('fiftyTwoWeekHigh', 'N/A'),
            '52 Week Low': info.get('fiftyTwoWeekLow', 'N/A'),
            'Market Cap': info.get('marketCap', 'N/A'),
            'Beta': info.get('beta', 'N/A')
        }
    
    def _get_valuation_metrics(self, stock):
        """Get valuation ratios and metrics"""
        info = stock.info
        return {
            'Trailing P/E': info.get('trailingPE', 'N/A'),
            'Forward P/E': info.get('forwardPE', 'N/A'),
            'PEG Ratio': info.get('pegRatio', 'N/A'),
            'Price to Book': info.get('priceToBook', 'N/A')
        }
    
    def _get_financial_health(self, stock):
        """Get financial health indicators"""
        info = stock.info
        return {
            'Total Debt': info.get('totalDebt', 'N/A'),
            'Debt to Equity': info.get('debtToEquity', 'N/A'),
            'Current Ratio': info.get('currentRatio', 'N/A'),
            'Total Revenue': info.get('totalRevenue', 'N/A'),
            'EBITDA': info.get('ebitda', 'N/A'),
        }
    
    def _get_profitability_metrics(self, stock):
        """Get profitability ratios"""
        info = stock.info
        return {
            'Profit Margin': self._format_percentage(info.get('profitMargins')),
            'Operating Margin': self._format_percentage(info.get('operatingMargins')),
            'Return on Equity (ROE)': self._format_percentage(info.get('returnOnEquity')),
        }
    
    def _get_growth_metrics(self, stock):
        """Get growth metrics"""
        info = stock.info
        return {
            'Revenue Growth': self._format_percentage(info.get('revenueGrowth')),
            'Earnings Growth': self._format_percentage(info.get('earningsGrowth')),
        }
    
    def _get_dividend_info(self, stock):
        """Get dividend information"""
        info = stock.info
        return {
            'Dividend Yield': self._format_percentage(info.get('dividendYield')),
            'Payout Ratio': self._format_percentage(info.get('payoutRatio')),
        }
    
    def _get_price_performance(self, stock):
        """Calculate price performance over different periods"""
        try:
            hist = stock.history(period="1y")
            if hist.empty:
                return {}
            
            current_price = hist['Close'].iloc[-1]
            
            performance = {}
            periods = {
                '1 Month': 30,
                '6 Months': 180,
                '1 Year': 365,
            }
            
            for period_name, days in periods.items():
                if len(hist) >= days:
                    try:
                        past_price = hist['Close'].iloc[-days]
                        return_pct = ((current_price - past_price) / past_price)
                        performance[period_name] = f"{return_pct:.2f}%"
                    except:
                        performance[period_name] = "N/A"
            
            return performance
        except:
            return {}
    
    def _get_analyst_info(self, stock):
        """Get analyst recommendations and targets"""
        info = stock.info
        return {
            'Target Mean Price': info.get('targetMeanPrice', 'N/A'),
            'Recommendation': info.get('recommendationKey', 'N/A'),
        }
    
    def _get_risk_metrics(self, stock):
        """Calculate risk metrics"""
        info = stock.info
        return {
            'Beta': info.get('beta', 'N/A'),
            '52 Week Change': self._format_percentage(info.get('52WeekChange')),
        }
    
    def _format_percentage(self, value):
        """Format decimal to percentage"""
        if value is None or value == 'N/A':
            return 'N/A'
        try:
            return f"{float(value) * 100:.2f}%"
        except:
            return 'N/A'
