'use client';

import React from 'react';
import dynamic from 'next/dynamic';

// Dynamically import Plotly to avoid SSR issues
const Plot = dynamic(() => import('react-plotly.js'), { ssr: false });

interface PriceChartProps {
    data: { Date: string; Close: number }[];
    symbol: string;
}

const PriceChart: React.FC<PriceChartProps> = ({ data, symbol }) => {
    if (!data || data.length === 0) return null;

    const xData = data.map(d => d.Date);
    const yData = data.map(d => d.Close);

    // Determine color based on trend (green if up, red if down)
    const startPrice = yData[0];
    const endPrice = yData[yData.length - 1];
    const color = endPrice >= startPrice ? '#10b981' : '#ef4444'; // emerald-500 or red-500

    return (
        <div className="glass-card p-6 rounded-2xl w-full h-[400px]">
            <h3 className="text-xl font-bold text-zinc-100 mb-4">Price History (1 Year)</h3>
            <div className="w-full h-full">
                <Plot
                    data={[
                        {
                            x: xData,
                            y: yData,
                            type: 'scatter',
                            mode: 'lines',
                            line: { color: color, width: 2 },
                            fill: 'tozeroy', // Create area chart effect
                            fillcolor: endPrice >= startPrice ? 'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.1)',
                            name: symbol,
                        },
                    ]}
                    layout={{
                        autosize: true,
                        paper_bgcolor: 'rgba(0,0,0,0)',
                        plot_bgcolor: 'rgba(0,0,0,0)',
                        font: { color: '#a1a1aa' }, // zinc-400
                        xaxis: {
                            showgrid: false,
                            zeroline: false,
                            showline: false,
                            tickformat: '%b %Y',
                        },
                        yaxis: {
                            showgrid: true,
                            gridcolor: 'rgba(255,255,255,0.05)',
                            zeroline: false,
                            tickprefix: '₹',
                        },
                        margin: { l: 40, r: 10, t: 10, b: 30 },
                        showlegend: false,
                        hovermode: 'x',
                    }}
                    useResizeHandler={true}
                    style={{ width: '100%', height: '100%' }}
                    config={{ displayModeBar: false }}
                />
            </div>
        </div>
    );
};

export default PriceChart;
