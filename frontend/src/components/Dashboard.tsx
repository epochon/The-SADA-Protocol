import React from 'react';
import MarketTicker from './MarketTicker';
import ChatInterface from './ChatInterface';

const Dashboard: React.FC = () => {
    return (
        <div className="flex flex-col h-screen w-full bg-zinc-950 text-zinc-100 font-sans overflow-hidden">
            {/* Top Navigation / Header */}
            <header className="flex items-center justify-between px-6 py-4 glass border-b border-zinc-800 z-10">
                <div className="flex items-center space-x-2">
                    <div className="w-8 h-8 rounded-full bg-emerald-500 flex items-center justify-center">
                        <span className="font-bold text-zinc-950">S</span>
                    </div>
                    <h1 className="text-xl font-bold tracking-tight text-glow">The SADA Protocol</h1>
                </div>
                <div className="flex items-center space-x-4">
                    <button className="px-4 py-2 text-sm font-medium text-zinc-400 hover:text-white transition-colors">
                        Dashboard
                    </button>
                    <button className="px-4 py-2 text-sm font-medium text-zinc-400 hover:text-white transition-colors">
                        Portfolio
                    </button>
                    <button className="px-4 py-2 text-sm font-medium text-zinc-400 hover:text-white transition-colors">
                        News
                    </button>
                    <div className="w-8 h-8 rounded-full bg-zinc-800 border border-zinc-700"></div>
                </div>
            </header>

            {/* Market Ticker */}
            <MarketTicker />

            {/* Main Content Areas */}
            <main className="flex-1 p-6 grid grid-cols-1 md:grid-cols-3 gap-6 overflow-y-auto">
                {/* Left Column: Portfolio & Stats */}
                <div className="md:col-span-2 space-y-6">
                    {/* Quick Stats Row */}
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                        <div className="glass-card p-4 rounded-xl">
                            <h3 className="text-zinc-400 text-sm">Total Balance</h3>
                            <p className="text-2xl font-bold text-white mt-1">$124,592.00</p>
                            <span className="text-emerald-400 text-xs">+2.4% today</span>
                        </div>
                        <div className="glass-card p-4 rounded-xl">
                            <h3 className="text-zinc-400 text-sm">Daily P&L</h3>
                            <p className="text-2xl font-bold text-emerald-400 mt-1">+$1,230.50</p>
                        </div>
                        <div className="glass-card p-4 rounded-xl">
                            <h3 className="text-zinc-400 text-sm">Risk Score</h3>
                            <p className="text-2xl font-bold text-yellow-400 mt-1">Moderate</p>
                        </div>
                    </div>

                    {/* Portfolio Chart Area */}
                    <div className="glass-card p-6 rounded-xl h-96 flex flex-col justify-center items-center text-zinc-500">
                        <p>Portfolio Performance Chart (Coming Soon)</p>
                    </div>
                </div>

                {/* Right Column: AI Chat Agent */}
                <div className="md:col-span-1">
                    <ChatInterface />
                </div>
            </main>
        </div>
    );
};

export default Dashboard;
