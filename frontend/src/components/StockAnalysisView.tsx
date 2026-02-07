'use client';

import React, { useState } from 'react';
import { Search, Download, TrendingUp, DollarSign, Activity, PieChart, AlertTriangle, ExternalLink } from 'lucide-react';
import PriceChart from './PriceChart';

const StockAnalysisView: React.FC = () => {
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
            const res = await fetch(`/api/report/analyze/${symbol}?exchange=${exchange}`);
            if (!res.ok) throw new Error('Failed to fetch analysis data');
            const result = await res.json();

            if (result.error) {
                throw new Error(result.error);
            }

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
        <div className="w-full h-full animate-in fade-in duration-500">
            {/* Search Bar - Agentic Style */}
            <div className="glass-card max-w-3xl mx-auto p-4 rounded-2xl mb-8 flex flex-col md:flex-row gap-3 border border-emerald-500/10 bg-zinc-900/40">
                <div className="flex-1 relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-zinc-500" size={18} />
                    <input
                        type="text"
                        placeholder="Enter Ticker (RELIANCE, TCS, AAPL...)"
                        value={symbol}
                        onChange={(e) => setSymbol(e.target.value.toUpperCase())}
                        className="w-full bg-zinc-950 border border-zinc-800 rounded-xl pl-10 pr-4 py-3 focus:outline-none focus:ring-1 focus:ring-emerald-500 transition-all uppercase text-sm font-mono tracking-wider"
                        onKeyDown={(e) => e.key === 'Enter' && analyzeStock()}
                    />
                </div>
                <select
                    value={exchange}
                    onChange={(e) => setExchange(e.target.value)}
                    className="bg-zinc-950 border border-zinc-800 rounded-xl px-4 py-3 focus:outline-none focus:ring-1 focus:ring-emerald-500 text-xs font-bold text-zinc-400"
                >
                    <option value="NSE">NSE</option>
                    <option value="BSE">BSE</option>
                    <option value="NASDAQ">NASDAQ</option>
                </select>
                <button
                    onClick={analyzeStock}
                    disabled={loading}
                    className="bg-emerald-600 hover:bg-emerald-500 text-zinc-950 font-bold py-3 px-8 rounded-xl transition-all disabled:opacity-50 flex items-center justify-center text-sm uppercase tracking-tighter"
                >
                    {loading ? 'Processing...' : 'Execute Analysis'}
                </button>
            </div>

            {/* Error State */}
            {error && (
                <div className="max-w-2xl mx-auto mb-8 p-4 bg-red-500/10 border border-red-500/20 text-red-400 rounded-xl flex items-center justify-center text-xs">
                    <AlertTriangle size={16} className="mr-2" /> {error}
                </div>
            )}

            {/* Initial Placeholder */}
            {!data && !loading && !error && (
                <div className="flex flex-col items-center justify-center py-20 text-center opacity-40">
                    <Activity size={64} className="text-zinc-700 mb-4 animate-pulse" />
                    <p className="max-w-xs text-zinc-500 text-sm">
                        Enter a stock symbol above to initiate a deep agentic scan of financial health and performance.
                    </p>
                </div>
            )}

            {/* Loading Placeholder */}
            {loading && (
                <div className="flex flex-col items-center justify-center py-20 text-center">
                    <div className="w-12 h-12 border-4 border-emerald-500/20 border-t-emerald-500 rounded-full animate-spin mb-4"></div>
                    <p className="text-emerald-500 animate-pulse font-mono text-sm">AGENT_SADA: FETCHING_MARKET_DATA...</p>
                </div>
            )}

            {/* Results Grid */}
            {data && (
                <div className="space-y-6 animate-in slide-in-from-bottom-2 duration-700">
                    {/* Company Summary Card */}
                    <div className="glass-card p-6 rounded-2xl border border-zinc-800 bg-zinc-900/30 flex flex-col md:flex-row justify-between items-center">
                        <div className="flex items-center gap-4">
                            <div className="w-12 h-12 rounded-xl bg-zinc-800 flex items-center justify-center text-xl font-bold border border-zinc-700">
                                {symbol[0]}
                            </div>
                            <div>
                                <h2 className="text-2xl font-bold text-white leading-tight">
                                    {data.company_profile?.['Company Name'] || symbol}
                                </h2>
                                <p className="text-zinc-500 text-xs flex items-center gap-2 mt-1">
                                    <span className="text-emerald-500 uppercase font-mono">{exchange}:{symbol}</span>
                                    <span>•</span>
                                    <span>{data.company_profile?.Sector || 'Unknown Sector'}</span>
                                </p>
                            </div>
                        </div>
                        <div className="text-right mt-4 md:mt-0">
                            <p className="text-zinc-500 text-[10px] uppercase font-bold tracking-widest">Active Price</p>
                            <p className="text-3xl font-mono font-bold text-emerald-400">
                                {exchange === 'NSE' || exchange === 'BSE' ? '₹' : '$'}{formatValue(data.current_market_data?.['Current Price'])}
                            </p>
                        </div>
                    </div>

                    {/* Chart Container */}
                    <div className="glass-card rounded-2xl h-[450px] overflow-hidden border border-zinc-800 bg-zinc-950 flex flex-col">
                        <div className="p-4 border-b border-zinc-800 flex justify-between items-center bg-zinc-900/20">
                            <span className="text-xs font-bold text-zinc-400 uppercase tracking-widest">Temporal Price Distribution (1Y)</span>
                            <div className="flex gap-2">
                                <button className="text-[10px] bg-emerald-500/10 text-emerald-500 px-2 py-1 rounded border border-emerald-500/20">AGENT_VERIFIED</button>
                            </div>
                        </div>
                        <div className="flex-1">
                            <PriceChart data={data.historical_prices} symbol={symbol} />
                        </div>
                    </div>

                    {/* Metric Cards Grid */}
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        <MetricCard title="VALUATION_ALGORITHMS" icon={<DollarSign size={16} />} metrics={data.valuation_metrics} color="text-blue-400" />
                        <MetricCard title="PROFITABILITY_INDICES" icon={<TrendingUp size={16} />} metrics={data.profitability_metrics} color="text-emerald-400" />
                        <MetricCard title="FINANCIAL_FORTITUDE" icon={<Activity size={16} />} metrics={data.financial_health} color="text-purple-400" />
                        <MetricCard title="GROWTH_VECTORS" icon={<TrendingUp size={16} />} metrics={data.growth_metrics} color="text-yellow-400" />
                        <MetricCard title="YIELD_COMPONENTS" icon={<PieChart size={16} />} metrics={data.dividend_info} color="text-pink-400" />

                        {/* Download Options - Unified Card */}
                        <div className="glass-card p-6 rounded-2xl border border-zinc-800 bg-zinc-900/20 flex flex-col justify-center items-center text-center">
                            <h3 className="text-sm font-bold text-zinc-100 mb-4 uppercase tracking-tighter">Export Intelligence</h3>
                            <div className="flex flex-col w-full gap-2">
                                <button onClick={() => downloadReport('excel')} className="text-xs font-bold py-2 bg-zinc-800 hover:bg-zinc-700 text-zinc-300 rounded-lg flex items-center justify-center transition-all">
                                    <Download size={14} className="mr-2" /> .XLSX REPORT
                                </button>
                                <button onClick={() => downloadReport('text')} className="text-xs font-bold py-2 bg-zinc-800 hover:bg-zinc-700 text-zinc-300 rounded-lg flex items-center justify-center transition-all">
                                    <Download size={14} className="mr-2" /> .TXT SUMMARY
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

const MetricCard = ({ title, icon, metrics, color }: any) => {
    if (!metrics) return null;
    return (
        <div className="glass-card p-5 rounded-2xl border border-zinc-800/50 bg-zinc-900/10 hover:border-zinc-700 transition-all">
            <div className={`flex items-center justify-between mb-4`}>
                <div className={`flex items-center ${color}`}>
                    {icon}
                    <h3 className="ml-2 font-bold text-xs text-zinc-300 tracking-widest">{title}</h3>
                </div>
                <div className="h-1 w-8 bg-zinc-800 rounded-full"></div>
            </div>
            <div className="space-y-3">
                {Object.entries(metrics).slice(0, 5).map(([key, value]: any) => (
                    <div key={key} className="flex justify-between items-center text-[11px] border-b border-zinc-800/30 pb-2 last:border-0 last:pb-0">
                        <span className="text-zinc-500 font-medium">{key}</span>
                        <span className="font-mono text-zinc-200 font-bold">{formatValue(value)}</span>
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

export default StockAnalysisView;
