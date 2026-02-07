'use client';

import React, { useEffect, useState } from 'react';
import { TrendingUp, TrendingDown, Loader2 } from 'lucide-react';

interface Stock {
    symbol: string;
    price: number;
    change: number;
    changePercent: number;
}

const MarketTicker: React.FC = () => {
    const [stocks, setStocks] = useState<Stock[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchMarketData = async () => {
            try {
                const res = await fetch('/api/market/ticker');
                if (!res.ok) throw new Error('Failed to fetch market data');
                const data = await res.json();
                setStocks(data);
            } catch (error) {
                console.error('Error fetching market data:', error);
                // Fallback or keep stale data
            } finally {
                setLoading(false);
            }
        };

        fetchMarketData();

        // Poll every 30 seconds to update prices
        const interval = setInterval(fetchMarketData, 30000);
        return () => clearInterval(interval);
    }, []);

    if (loading && stocks.length === 0) {
        return (
            <div className="w-full bg-zinc-900/50 border-b border-zinc-800 py-2 flex justify-center text-zinc-500 text-xs">
                <Loader2 className="animate-spin mr-2" size={14} /> Loading Market Data...
            </div>
        );
    }

    // If fetch failed but we have no data, maybe show empty or error?
    // For scrolling marquee, we need at least some content.
    // If empty, show nothing or placeholder.
    if (stocks.length === 0) return null;

    return (
        <div className="w-full bg-zinc-900/50 border-b border-zinc-800 overflow-hidden py-2 relative">
            <div className="flex animate-marquee whitespace-nowrap hover:pause">
                {/* Render twice for seamless loop */}
                {[...stocks, ...stocks].map((stock, index) => (
                    <div key={`${stock.symbol}-${index}`} className="flex items-center mx-6 space-x-2">
                        <span className="font-bold text-zinc-300">{stock.symbol}</span>
                        <span className="text-zinc-400">${stock.price.toFixed(2)}</span>
                        <span className={`flex items-center text-xs ${stock.change >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                            {stock.change >= 0 ? <TrendingUp size={12} className="mr-1" /> : <TrendingDown size={12} className="mr-1" />}
                            {stock.change > 0 ? '+' : ''}{stock.changePercent.toFixed(2)}%
                        </span>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default MarketTicker;
