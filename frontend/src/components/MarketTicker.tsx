import React from 'react';
import { TrendingUp, TrendingDown } from 'lucide-react';

interface Stock {
    symbol: string;
    price: number;
    change: number;
    changePercent: number;
}

const mockStocks: Stock[] = [
    { symbol: 'AAPL', price: 175.43, change: 1.25, changePercent: 0.72 },
    { symbol: 'BTC', price: 64230.50, change: -120.50, changePercent: -0.19 },
    { symbol: 'ETH', price: 3450.20, change: 45.10, changePercent: 1.32 },
    { symbol: 'NVDA', price: 890.15, change: 15.40, changePercent: 1.76 },
    { symbol: 'TSLA', price: 168.90, change: -2.30, changePercent: -1.34 },
    { symbol: 'SPX', price: 5120.45, change: 10.20, changePercent: 0.20 },
];

const MarketTicker: React.FC = () => {
    return (
        <div className="w-full bg-zinc-900/50 border-b border-zinc-800 overflow-hidden py-2">
            <div className="flex animate-marquee whitespace-nowrap">
                {/* Render twice for seamless loop */}
                {[...mockStocks, ...mockStocks].map((stock, index) => (
                    <div key={index} className="flex items-center mx-6 space-x-2">
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
