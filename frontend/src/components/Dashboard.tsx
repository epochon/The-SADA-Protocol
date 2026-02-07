'use client';

import React, { useState, useEffect } from 'react';
import MarketTicker from './MarketTicker';
import ChatInterface from './ChatInterface';
import PriceChart from './PriceChart';
import RiskProfileQuestionnaire from './RiskProfileQuestionnaire';
import StockAnalysisView from './StockAnalysisView';
import HypeSlayerView from './HypeSlayerView';
import DasAIView from './DasAIView';

const Dashboard: React.FC = () => {
    const [view, setView] = useState<'dashboard' | 'risk-profiler' | 'analysis' | 'hypeslayer' | 'das-ai'>('hypeslayer');
    const [riskProfile, setRiskProfile] = useState<any>(null);

    useEffect(() => {
        // Hydration safe check
        if (typeof window !== 'undefined') {
            const savedProfile = localStorage.getItem('hypeslayer-risk-profile');
            if (savedProfile) {
                try {
                    setRiskProfile(JSON.parse(savedProfile));
                } catch (e) {
                    console.error("Failed to parse risk profile");
                }
            }
        }
    }, [view]); // Re-check on view change in case it was updated in profiler

    const sampleChartData = [
        { Date: '2023-01-01', Close: 15420 },
        { Date: '2023-02-01', Close: 15800 },
        { Date: '2023-03-01', Close: 16200 },
        { Date: '2023-04-01', Close: 15900 },
        { Date: '2023-05-01', Close: 16500 },
        { Date: '2023-06-01', Close: 17200 },
        { Date: '2023-07-01', Close: 17800 },
        { Date: '2023-08-01', Close: 17400 },
        { Date: '2023-09-01', Close: 18100 },
        { Date: '2023-10-01', Close: 18900 },
        { Date: '2023-11-01', Close: 19500 },
        { Date: '2023-12-01', Close: 20200 },
    ];

    return (
        <div className="flex flex-col h-screen w-full bg-zinc-950 text-zinc-100 font-sans overflow-hidden">
            {/* Top Navigation / Header */}
            <header className="flex items-center justify-between px-6 py-4 glass border-b border-zinc-800 z-10">
                <div className="flex items-center space-x-2">
                    <div className="w-8 h-8 rounded-full bg-emerald-500 flex items-center justify-center">
                        <span className="font-bold text-zinc-950">D</span>
                    </div>
                    <div className="flex flex-col">
                        <h1 className="text-xl font-bold tracking-tight text-glow leading-none">DAS The HypeSlayer</h1>
                        <span className="text-[10px] text-emerald-500 font-mono tracking-widest uppercase mt-1">AI Financial Agent</span>
                    </div>
                </div>
                <div className="flex items-center space-x-1">
                    <button
                        onClick={() => setView('das-ai')}
                        className={`px-4 py-2 text-sm font-medium transition-all rounded-lg ${view === 'das-ai' ? 'text-white bg-zinc-800/50' : 'text-zinc-400 hover:text-white hover:bg-zinc-900'}`}
                    >
                        Das AI
                    </button>
                    <button
                        onClick={() => setView('hypeslayer')}
                        className={`px-4 py-2 text-sm font-medium transition-all rounded-lg ${view === 'hypeslayer' ? 'text-white bg-zinc-800/50' : 'text-zinc-400 hover:text-white hover:bg-zinc-900'}`}
                    >
                        HypeSlayer
                    </button>
                    <button
                        onClick={() => setView('dashboard')}
                        className={`px-4 py-2 text-sm font-medium transition-all rounded-lg ${view === 'dashboard' ? 'text-white bg-zinc-800/50' : 'text-zinc-400 hover:text-white hover:bg-zinc-900'}`}
                    >
                        Dashboard
                    </button>
                    <button
                        onClick={() => setView('risk-profiler')}
                        className={`px-4 py-2 text-sm font-medium transition-all rounded-lg ${view === 'risk-profiler' ? 'text-white bg-zinc-800/50' : 'text-zinc-400 hover:text-white hover:bg-zinc-900'}`}
                    >
                        Risk Profiler
                    </button>
                    <button
                        onClick={() => setView('analysis')}
                        className={`px-4 py-2 text-sm font-medium transition-all rounded-lg ${view === 'analysis' ? 'text-white bg-zinc-800/50' : 'text-zinc-400 hover:text-white hover:bg-zinc-900'}`}
                    >
                        Stock Analysis
                    </button>
                    <div className="ml-4 w-8 h-8 rounded-full bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-500">
                        <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></div>
                    </div>
                </div>
            </header>

            {/* Market Ticker */}
            <MarketTicker />

            {/* Main Content Areas */}
            <main className="flex-1 p-6 overflow-y-auto relative bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-zinc-900/50 via-zinc-950 to-zinc-950">
                {view === 'das-ai' && (
                    <div className="h-full">
                        <DasAIView />
                    </div>
                )}

                {view === 'hypeslayer' && (
                    <div className="h-full">
                        <HypeSlayerView />
                    </div>
                )}

                {view === 'dashboard' && (
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 h-full">
                        {/* Left Column: Portfolio & Stats */}
                        <div className="md:col-span-2 space-y-6">
                            {/* Quick Stats Row */}
                            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                                <div className="glass-card p-4 rounded-xl border border-zinc-800/50 bg-zinc-900/20">
                                    <h3 className="text-zinc-400 text-xs font-medium uppercase tracking-wider">Total Balance</h3>
                                    <p className="text-2xl font-bold text-white mt-1">$124,592.00</p>
                                    <span className="text-emerald-400 text-xs font-medium">+2.4% today</span>
                                </div>
                                <div className="glass-card p-4 rounded-xl border border-zinc-800/50 bg-zinc-900/20">
                                    <h3 className="text-zinc-400 text-xs font-medium uppercase tracking-wider">Daily P&L</h3>
                                    <p className="text-2xl font-bold text-emerald-400 mt-1">+$1,230.50</p>
                                </div>
                                <div className="glass-card p-4 rounded-xl border border-zinc-800/50 bg-zinc-900/20 cursor-pointer hover:border-emerald-500/30 transition-all" onClick={() => setView('risk-profiler')}>
                                    <h3 className="text-zinc-400 text-xs font-medium uppercase tracking-wider">Risk Profile</h3>
                                    <p className={`text-2xl font-bold mt-1 ${!riskProfile ? 'text-yellow-400' :
                                        riskProfile.category === 'Conservative' ? 'text-blue-400' :
                                            riskProfile.category === 'Moderate' ? 'text-emerald-400' :
                                                'text-red-400'
                                        }`}>
                                        {riskProfile?.category || 'Not Set'}
                                    </p>
                                    <span className="text-zinc-500 text-[10px]">{riskProfile ? 'Click to re-assess →' : 'Click to configure →'}</span>
                                </div>
                            </div>

                            {/* Portfolio Chart Area */}
                            <div className="glass-card p-6 rounded-xl h-[500px] flex flex-col items-center justify-center border border-zinc-800/50 bg-zinc-900/20 relative overflow-hidden group">
                                <div className="absolute inset-0 bg-gradient-to-br from-emerald-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
                                <PriceChart data={sampleChartData} symbol="MARKET_INDEX" />
                            </div>
                        </div>

                        {/* Right Column: AI Chat Agent */}
                        <div className="md:col-span-1 h-full min-h-[600px]">
                            <ChatInterface />
                        </div>
                    </div>
                )}

                {view === 'risk-profiler' && (
                    <div className="max-w-4xl mx-auto h-full pb-10">
                        <RiskProfileQuestionnaire />
                    </div>
                )}

                {view === 'analysis' && (
                    <div className="h-full">
                        <StockAnalysisView />
                    </div>
                )}
            </main>
        </div>
    );
};

export default Dashboard;
