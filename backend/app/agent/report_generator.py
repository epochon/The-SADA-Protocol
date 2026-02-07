"""
Financial Report Generator
Exports comprehensive stock analysis to multiple formats
"""

import pandas as pd
from datetime import datetime
import os
import io

class ReportGenerator:
    """
    Generates comprehensive financial reports in multiple formats
    """
    
    def __init__(self, stock_data):
        """
        Initialize with stock analysis data
        
        Args:
            stock_data: Dictionary from StockAnalysisAgent.analyze_stock()
        """
        self.data = stock_data
        self.symbol = stock_data['symbol']
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def generate_excel_report(self):
        """
        Generate comprehensive Excel report with multiple sheets
        Returns: BytesIO object containing the Excel file
        """
        output = io.BytesIO()
        
        # Create Excel writer
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            
            # Sheet 1: Overview & Summary
            self._create_overview_sheet(writer)
            
            # Sheet 2: Company Profile
            self._create_profile_sheet(writer)
            
            # Sheet 3: Current Market Data
            self._create_market_data_sheet(writer)
            
            # Sheet 4: Valuation Metrics
            self._create_valuation_sheet(writer)
            
            # Sheet 5: Financial Health
            self._create_financial_health_sheet(writer)
            
            # Sheet 6: Profitability Metrics
            self._create_profitability_sheet(writer)
            
            # Sheet 7: Growth Metrics
            self._create_growth_sheet(writer)
            
            # Sheet 8: Dividend Information
            self._create_dividend_sheet(writer)
            
            # Sheet 9: Price Performance
            self._create_performance_sheet(writer)
            
            # Sheet 14: Risk Metrics
            self._create_risk_sheet(writer)
            
            # Sheet 15: Analyst Information
            self._create_analyst_sheet(writer)
        
        output.seek(0)
        return output
    
    def _create_overview_sheet(self, writer):
        """Create overview summary sheet"""
        df_data = []
        
        # Header
        df_data.append(['COMPREHENSIVE FINANCIAL REPORT', ''])
        df_data.append(['Company Symbol', self.symbol])
        df_data.append(['Exchange', self.data.get('exchange', 'N/A')])
        df_data.append(['Report Generated', self.data.get('timestamp', 'N/A')])
        df_data.append(['', ''])
        
        # Company basics
        profile = self.data['company_profile']
        df_data.append(['COMPANY INFORMATION', ''])
        df_data.append(['Company Name', profile.get('Company Name', 'N/A')])
        df_data.append(['Sector', profile.get('Sector', 'N/A')])
        df_data.append(['Industry', profile.get('Industry', 'N/A')])
        df_data.append(['', ''])
        
        # Key metrics
        market = self.data['current_market_data']
        df_data.append(['KEY METRICS', ''])
        df_data.append(['Current Price', market.get('Current Price', 'N/A')])
        df_data.append(['Market Cap', market.get('Market Cap', 'N/A')])
        df_data.append(['52 Week High', market.get('52 Week High', 'N/A')])
        df_data.append(['52 Week Low', market.get('52 Week Low', 'N/A')])
        df_data.append(['', ''])
        
        # Valuation
        valuation = self.data['valuation_metrics']
        df_data.append(['VALUATION RATIOS', ''])
        df_data.append(['P/E Ratio', valuation.get('Trailing P/E', 'N/A')])
        df_data.append(['P/B Ratio', valuation.get('Price to Book', 'N/A')])
        df_data.append(['', ''])
        
        # Profitability
        profit = self.data['profitability_metrics']
        df_data.append(['PROFITABILITY', ''])
        df_data.append(['ROE', profit.get('Return on Equity (ROE)', 'N/A')])
        df_data.append(['Profit Margin', profit.get('Profit Margin', 'N/A')])
        
        df = pd.DataFrame(df_data, columns=['Metric', 'Value'])
        df.to_excel(writer, sheet_name='Overview', index=False)
    
    def _create_profile_sheet(self, writer):
        """Create company profile sheet"""
        profile = self.data['company_profile']
        df = pd.DataFrame(list(profile.items()), columns=['Field', 'Value'])
        df.to_excel(writer, sheet_name='Company Profile', index=False)
    
    def _create_market_data_sheet(self, writer):
        """Create current market data sheet"""
        market = self.data['current_market_data']
        df = pd.DataFrame(list(market.items()), columns=['Metric', 'Value'])
        df.to_excel(writer, sheet_name='Current Market Data', index=False)
    
    def _create_valuation_sheet(self, writer):
        """Create valuation metrics sheet"""
        valuation = self.data['valuation_metrics']
        df = pd.DataFrame(list(valuation.items()), columns=['Metric', 'Value'])
        df.to_excel(writer, sheet_name='Valuation Metrics', index=False)
    
    def _create_financial_health_sheet(self, writer):
        """Create financial health sheet"""
        health = self.data['financial_health']
        df = pd.DataFrame(list(health.items()), columns=['Metric', 'Value'])
        df.to_excel(writer, sheet_name='Financial Health', index=False)
    
    def _create_profitability_sheet(self, writer):
        """Create profitability metrics sheet"""
        profit = self.data['profitability_metrics']
        df = pd.DataFrame(list(profit.items()), columns=['Metric', 'Value'])
        df.to_excel(writer, sheet_name='Profitability', index=False)
    
    def _create_growth_sheet(self, writer):
        """Create growth metrics sheet"""
        growth = self.data['growth_metrics']
        df = pd.DataFrame(list(growth.items()), columns=['Metric', 'Value'])
        df.to_excel(writer, sheet_name='Growth Metrics', index=False)
    
    def _create_dividend_sheet(self, writer):
        """Create dividend information sheet"""
        dividend = self.data['dividend_info']
        df = pd.DataFrame(list(dividend.items()), columns=['Metric', 'Value'])
        df.to_excel(writer, sheet_name='Dividend Info', index=False)
    
    def _create_performance_sheet(self, writer):
        """Create price performance sheet"""
        performance = self.data['price_performance']
        df = pd.DataFrame(list(performance.items()), columns=['Period', 'Return'])
        df.to_excel(writer, sheet_name='Price Performance', index=False)
    
    def _create_risk_sheet(self, writer):
        """Create risk metrics sheet"""
        risk = self.data['risk_metrics']
        df = pd.DataFrame(list(risk.items()), columns=['Metric', 'Value'])
        df.to_excel(writer, sheet_name='Risk Metrics', index=False)
    
    def _create_analyst_sheet(self, writer):
        """Create analyst information sheet"""
        analyst = self.data['analyst_info']
        df = pd.DataFrame(list(analyst.items()), columns=['Metric', 'Value'])
        df.to_excel(writer, sheet_name='Analyst Info', index=False)
