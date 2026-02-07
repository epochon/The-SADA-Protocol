'use client';

import React, { useState } from 'react';
import { Search, Download, TrendingUp, DollarSign, Activity, PieChart, AlertTriangle } from 'lucide-react';

const StockAnalysis: React.FC = () => {
    const [symbol, setSymbol] = useState('');
    const [exchange, setExchange] = useState('NSE');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [data, setData] = useState<any>(null);

    const analyzeStock = async () => {
        if (!symbol) return;
        setLoading(true);
        setError(null);
        setData(null);

        try {
            // Using the agent tool indirectly via a new endpoint or adapting the existing agent logic? 
            // We can create a direct analysis endpoint or reuse the report logic. 
            // Let's assume we made a direct analysis endpoint based on the Python logic provided.
            // Wait, I need to expose a JSON analysis endpoint in backend first!
            // I'll add /api/report/analyze/{symbol} to return JSON data.

            const res = await fetch(`/api/report/analyze/${symbol}?exchange=${exchange}`);
            if (!res.ok) throw new Error('Failed to fetch analysis data');
            const result = await res.json();
            setData(result);
        } catch (err: any) {
            setError(err.message || 'Analysis failed');
        } finally {
            setLoading(false);
        }
    };

    const downloadReport = (format: string) => {
        if (!symbol) return;
        window.open(`/api/report/download/${symbol}?exchange=${exchange}&format=${format}`, '_blank');
    };

    return (
        <div className="min-h-screen bg-zinc-950 text-zinc-100 p-8 font-sans">
            <div className="max-w-7xl mx-auto">
                {/* Header */}
                <div className="text-center mb-12">
                    <h1 className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-cyan-500 mb-4">
                        Indian Stock Market Analysis
                    </h1>
                    <p className="text-zinc-400 text-lg">
                        Get comprehensive financial reports for any NSE/BSE listed company
                    </p>
                </div>

                {/* Search Bar */}
                <div className="glass-card max-w-2xl mx-auto p-6 rounded-2xl mb-12 flex flex-col md:flex-row gap-4">
                    <input
                        type="text"
                        placeholder="Enter Stock Symbol (e.g., RELIANCE, TCS)"
                        value={symbol}
                        onChange={(e) => setSymbol(e.target.value.toUpperCase())}
                        className="flex-1 bg-zinc-900 border border-zinc-700 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-emerald-500 transition-all uppercase placeholder-zinc-500"
                        onKeyDown={(e) => e.key === 'Enter' && analyzeStock()}
                    />
                    <select
                        value={exchange}
                        onChange={(e) => setExchange(e.target.value)}
                        className="bg-zinc-900 border border-zinc-700 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-emerald-500"
                    >
                        <option value="NSE">NSE</option>
                        <option value="BSE">BSE</option>
                    </select>
                    <button
                        onClick={analyzeStock}
                        disabled={loading}
                        className="bg-emerald-600 hover:bg-emerald-500 text-white font-semibold py-3 px-8 rounded-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
                    >
                        {loading ? 'Analyzing...' : <><Search size={20} className="mr-2" /> Analyze</>}
                    </button>
                </div>

                {/* Error State */}
                {error && (
                    <div className="max-w-2xl mx-auto mb-8 p-4 bg-red-500/10 border border-red-500/20 text-red-400 rounded-xl flex items-center justify-center">
                        <AlertTriangle size={20} className="mr-2" /> {error}
                    </div>
                )}

                {/* Results */}
                {data && (
                    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
                        {/* Company Header */}
                        <div className="glass-card p-8 rounded-2xl bg-gradient-to-br from-emerald-900/20 to-zinc-900/50 border border-emerald-500/20">
                            <div className="flex flex-col md:flex-row justify-between items-start md:items-center">
                                <div>
                                    <h2 className="text-3xl font-bold text-white mb-2">{data.company_profile['Company Name']}</h2>
                                    <div className="flex items-center space-x-3 text-zinc-400">
                                        <span className="bg-zinc-800 px-2 py-1 rounded text-xs">{data.exchange}:{data.symbol}</span>
                                        <span>{data.company_profile.Sector}</span>
                                        <span>•</span>
                                        <span>{data.company_profile.Industry}</span>
                                    </div>
                                </div>
                                <div className="mt-4 md:mt-0 text-right">
                                    <div className="text-4xl font-mono font-bold text-emerald-400">
                                        ₹{formatValue(data.current_market_data['Current Price'])}
                                    </div>
                                    <div className="text-zinc-400 text-sm mt-1">Current Price</div>
                                </div>
                            </div>
                        </div>

                        {/* Grid Metrics */}
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                            {/* Valuation */}
                            <MetricCard title="Valuation" icon={<DollarSign size={20} />} metrics={data.valuation_metrics} color="text-blue-400" />
                            {/* Profitability */}
                            <MetricCard title="Profitability" icon={<TrendingUp size={20} />} metrics={data.profitability_metrics} color="text-emerald-400" />
                            {/* Financial Health */}
                            <MetricCard title="Financial Health" icon={<Activity size={20} />} metrics={data.financial_health} color="text-purple-400" />
                            {/* Growth */}
                            <MetricCard title="Growth" icon={<TrendingUp size={20} />} metrics={data.growth_metrics} color="text-yellow-400" />
                            {/* Dividends */}
                            <MetricCard title="Dividends" icon={<PieChart size={20} />} metrics={data.dividend_info} color="text-pink-400" />
                            {/* Performance */}
                            <MetricCard title="Performance" icon={<TrendingUp size={20} />} metrics={data.price_performance} color="text-orange-400" />
                        </div>

                        {/* Download Section */}
                        <div className="glass-card p-8 rounded-2xl text-center">
                            <h3 className="text-2xl font-bold mb-4">Download Detailed Report</h3>
                            <p className="text-zinc-400 mb-6">Get complete financial statements, historical data, and deep analysis.</p>
                            <div className="flex flex-wrap justify-center gap-4">
                                <button onClick={() => downloadReport('excel')} className="flex items-center px-6 py-3 bg-green-600 hover:bg-green-500 rounded-xl font-medium transition-all">
                                    <Download size={18} className="mr-2" /> Excel Report
                                </button>
                                <button onClick={() => downloadReport('csv')} className="flex items-center px-6 py-3 bg-blue-600 hover:bg-blue-500 rounded-xl font-medium transition-all">
                                    <Download size={18} className="mr-2" /> CSV Data (ZIP)
                                </button>
                                <button onClick={() => downloadReport('text')} className="flex items-center px-6 py-3 bg-zinc-700 hover:bg-zinc-600 rounded-xl font-medium transition-all">
                                    <Download size={18} className="mr-2" /> Text Summary
                                </button>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

const MetricCard = ({ title, icon, metrics, color }: any) => {
    if (!metrics) return null;
    return (
        <div className="glass-card p-6 rounded-2xl hover:border-zinc-600 transition-colors">
            <div className={`flex items-center mb-4 ${color}`}>
                {icon}
                <h3 className="ml-2 font-bold text-lg text-zinc-100">{title}</h3>
            </div>
            <div className="space-y-3">
                {Object.entries(metrics).slice(0, 5).map(([key, value]: any) => (
                    <div key={key} className="flex justify-between items-center text-sm border-b border-zinc-800/50 pb-2 last:border-0 last:pb-0">
                        <span className="text-zinc-400">{key}</span>
                        <span className="font-mono font-medium">{formatValue(value)}</span>
                    </div>
                ))}
            </div>
        </div>
    );
};

function formatValue(value: any) {
    if (value === null || value === undefined || value === 'N/A') return 'N/A';
    if (typeof value === 'number') {
        return value.toLocaleString('en-IN', { maximumFractionDigits: 2 });
    }
    return value;
}

export default StockAnalysis;
