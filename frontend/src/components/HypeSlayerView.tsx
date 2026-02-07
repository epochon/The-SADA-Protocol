'use client';

import React, { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { Youtube, Shield, AlertTriangle, CheckCircle, Search, Terminal, MessageSquare, ArrowRight, ShieldAlert, BrainCircuit } from 'lucide-react';

const HypeSlayerView: React.FC = () => {
    const [videoUrl, setVideoUrl] = useState('');

    const mutation = useMutation({
        mutationFn: async (url: string) => {
            const res = await fetch('/api/hypeslayer/analyze-video', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ video_url: url })
            });

            if (!res.ok) throw new Error('Analysis failed. Please check the URL or server status.');
            return res.json();
        }
    });

    const analysis = mutation.data;
    const loading = mutation.isPending;
    const error = mutation.error;

    const startAnalysis = () => {
        if (!videoUrl) return;
        mutation.mutate(videoUrl);
    };

    return (
        <div className="w-full h-full animate-in fade-in duration-700">
            {/* Input Phase */}
            {!analysis && !loading && (
                <div className="max-w-3xl mx-auto py-20">
                    <div className="text-center mb-10">
                        <div className="inline-flex items-center justify-center p-4 bg-emerald-500/10 border border-emerald-500/20 rounded-3xl mb-6">
                            <Shield className="text-emerald-500 w-12 h-12" />
                        </div>
                        <h2 className="text-4xl font-black text-white mb-4 tracking-tighter uppercase italic">
                            Reality Check <span className="text-emerald-500">Protocol</span>
                        </h2>
                        <p className="text-zinc-500 text-lg max-w-xl mx-auto">
                            Examine financial claims from YouTube videos. Our agentic pipeline verifies facts, detects hyperbolic hype, and flags predatory patterns.
                        </p>
                    </div>

                    <div className="glass-card p-6 rounded-[2.5rem] border border-emerald-500/20 bg-zinc-900/40 shadow-2xl shadow-emerald-950/20">
                        <div className="flex flex-col md:flex-row gap-4">
                            <div className="flex-1 relative">
                                <Youtube className="absolute left-4 top-1/2 transform -translate-y-1/2 text-red-500" size={24} />
                                <input
                                    type="text"
                                    placeholder="Paste YouTube Video URL..."
                                    value={videoUrl}
                                    onChange={(e) => setVideoUrl(e.target.value)}
                                    className="w-full bg-zinc-950 border border-zinc-800 rounded-2xl pl-14 pr-4 py-5 focus:outline-none focus:ring-1 focus:ring-emerald-500 transition-all text-sm font-medium"
                                />
                            </div>
                            <button
                                onClick={startAnalysis}
                                className="bg-emerald-600 hover:bg-emerald-500 text-zinc-950 px-10 py-5 rounded-2xl font-black uppercase tracking-widest text-xs transition-all flex items-center justify-center group"
                            >
                                Initiate Scan <ArrowRight className="ml-2 group-hover:translate-x-1 transition-transform" size={16} />
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Loading Phase - Agent Thinking */}
            {loading && (
                <div className="max-w-4xl mx-auto py-20 text-center">
                    <div className="relative inline-block mb-10">
                        <div className="w-24 h-24 border-2 border-emerald-500/10 rounded-full"></div>
                        <div className="absolute inset-0 w-24 h-24 border-t-2 border-emerald-500 rounded-full animate-spin"></div>
                        <BrainCircuit className="absolute inset-0 m-auto text-emerald-500 animate-pulse" size={32} />
                    </div>
                    <h3 className="text-2xl font-mono text-emerald-500 mb-2 uppercase tracking-widest">SADA_AGENT.deliberating()</h3>
                    <p className="text-zinc-500 font-mono text-xs animate-pulse">EXTRACTING_TRANSCRIPT // CALCULATING_CONFIDENCE // VERIFYING_EXTERNAL_DATA</p>
                </div>
            )}

            {/* Results Phase */}
            {analysis && (
                analysis.decision === 'REFUSE' && analysis.entities?.video_topic === 'unrelated' ? (
                    <div className="max-w-2xl mx-auto py-20 text-center animate-in fade-in zoom-in duration-500">
                        <div className="inline-flex items-center justify-center p-6 bg-red-500/10 border border-red-500/30 rounded-full mb-6">
                            <ShieldAlert className="text-red-500 w-16 h-16" />
                        </div>
                        <h2 className="text-3xl font-black text-white mb-4 uppercase tracking-tight">Protocol Violation Detected</h2>
                        <div className="bg-red-950/30 border border-red-900/50 p-6 rounded-2xl max-w-lg mx-auto">
                            <p className="text-red-200 font-mono text-sm leading-relaxed mb-4">
                                "The agent has determined this content is UNRELATED to financial markets, economics, or investment analysis."
                            </p>
                            <div className="flex items-center justify-center gap-2 text-xs text-red-400 font-bold uppercase tracking-widest bg-red-950/50 p-2 rounded">
                                <AlertTriangle size={12} /> Topic: {analysis.entities?.video_topic || "Unknown"}
                            </div>
                        </div>
                        <button
                            onClick={() => { mutation.reset(); setVideoUrl(''); }}
                            className="mt-8 px-8 py-3 bg-zinc-800 hover:bg-zinc-700 text-zinc-300 rounded-xl font-bold uppercase tracking-widest text-xs transition-colors border border-zinc-700"
                        >
                            Submit New URL
                        </button>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 h-full pb-10">
                        {/* Left Column: Decision & Summary */}
                        <div className="lg:col-span-8 space-y-6">
                            <div className={`glass-card p-8 rounded-3xl border ${analysis.decision === 'VERIFY' ? 'border-emerald-500/30 bg-emerald-500/5' : 'border-red-500/30 bg-red-500/5'}`}>
                                <div className="flex items-start justify-between">
                                    <div>
                                        <div className="flex items-center gap-3 mb-2">
                                            <span className={`px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-widest ${analysis.decision === 'VERIFY' ? 'bg-emerald-500 text-zinc-950' : 'bg-red-500 text-white'}`}>
                                                FINAL_DECISION: {analysis.decision}
                                            </span>
                                            <span className="text-zinc-500 text-[10px] font-mono">CONFIDENCE: {Math.round(analysis.confidence_score)}%</span>
                                        </div>
                                        <h2 className="text-3xl font-black text-white leading-tight">
                                            {analysis.entities?.claim || analysis.entities?.primary_claim || "Financial Reality Assessment"}
                                        </h2>
                                        <p className="text-zinc-400 mt-4 text-sm leading-relaxed max-w-2xl">
                                            {analysis.confidence?.reasoning || "Agent analysis complete. Please review the deliberation log for detailed breakdown."}
                                        </p>
                                    </div>
                                    <div className="hidden md:block">
                                        {analysis.decision === 'VERIFY' ? <CheckCircle className="text-emerald-500" size={64} /> : <ShieldAlert className="text-red-500" size={64} />}
                                    </div>
                                </div>
                            </div>

                            {/* Real-world Data Check */}
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div className="glass-card p-6 rounded-2xl border border-zinc-800 bg-zinc-900/20">
                                    <h4 className="text-zinc-500 text-[10px] font-black uppercase tracking-widest mb-4">MARKET_REALITY_SOURCE</h4>
                                    <div className="flex items-center justify-between">
                                        <div>
                                            <p className="text-zinc-400 text-xs uppercase">{analysis.verification?.ticker || "ASSET"}</p>
                                            <p className="text-2xl font-mono font-bold text-white">
                                                ${analysis.verification?.real_data?.current_price || "---"}
                                            </p>
                                        </div>
                                        <div className="text-right">
                                            <p className="text-zinc-500 text-[10px] uppercase">ANALYSIS</p>
                                            <p className={`text-sm font-bold ${analysis.verification?.verification_status === 'corroborated' ? 'text-emerald-400' : 'text-red-400'}`}>
                                                {analysis.verification?.verification_status?.toUpperCase() || "UNVERIFIED"}
                                            </p>
                                        </div>
                                    </div>
                                </div>
                                <div className="glass-card p-6 rounded-2xl border border-zinc-800 bg-zinc-900/20">
                                    <h4 className="text-zinc-500 text-[10px] font-black uppercase tracking-widest mb-4">PSYCHOLOGY_DETECTION</h4>
                                    <div className="flex items-center justify-between">
                                        <div>
                                            <p className="text-zinc-400 text-xs uppercase">HYPE_LEVEL</p>
                                            <p className={`text-2xl font-black ${analysis.sentiment?.hype_level === 'EXTREME' || analysis.sentiment?.hype_level === 'HIGH' ? 'text-red-500' : 'text-emerald-500'}`}>
                                                {analysis.sentiment?.hype_level || "UNKNOWN"}
                                            </p>
                                        </div>
                                        <div className="text-right">
                                            <p className="text-zinc-500 text-[10px] uppercase">PENALTY</p>
                                            <p className="text-sm font-bold text-zinc-300">-{analysis.sentiment?.hype_penalty || 0}</p>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            {/* Highlights & Claims Analysis */}
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                {/* Suspicious Claims */}
                                <div className="glass-card p-6 rounded-2xl border border-red-500/20 bg-red-500/5">
                                    <h4 className="text-red-400 text-[10px] font-black uppercase tracking-widest mb-4 flex items-center gap-2">
                                        <AlertTriangle size={14} /> DETECTED_HYPE_SIGNALS
                                    </h4>
                                    <ul className="space-y-3">
                                        {analysis.entities?.suspicious_claims?.length > 0 ? (
                                            analysis.entities.suspicious_claims.map((claim: string, i: number) => (
                                                <li key={i} className="text-xs text-red-200/80 bg-red-500/10 p-2 rounded border border-red-500/10">
                                                    "{claim}"
                                                </li>
                                            ))
                                        ) : (
                                            <li className="text-xs text-zinc-500 italic">No specific hype signals detected.</li>
                                        )}
                                    </ul>
                                </div>

                                {/* Valid Points */}
                                <div className="glass-card p-6 rounded-2xl border border-emerald-500/20 bg-emerald-500/5">
                                    <h4 className="text-emerald-400 text-[10px] font-black uppercase tracking-widest mb-4 flex items-center gap-2">
                                        <CheckCircle size={14} /> VERIFIED_CONCEPTS
                                    </h4>
                                    <ul className="space-y-3">
                                        {analysis.entities?.valid_points?.length > 0 ? (
                                            analysis.entities.valid_points.map((point: string, i: number) => (
                                                <li key={i} className="text-xs text-emerald-200/80 bg-emerald-500/10 p-2 rounded border border-emerald-500/10">
                                                    "{point}"
                                                </li>
                                            ))
                                        ) : (
                                            <li className="text-xs text-zinc-500 italic">No specific valid points extracted.</li>
                                        )}
                                    </ul>
                                </div>
                            </div>

                            {/* Transcript Highlights */}
                            <div className="glass-card p-6 rounded-2xl border border-zinc-800 bg-zinc-900/10">
                                <h4 className="text-zinc-500 text-[10px] font-black uppercase tracking-widest mb-4">SOURCE_TRANSCRIPT_FRAGMENT</h4>
                                <div className="max-h-40 overflow-y-auto pr-2 custom-scrollbar italic text-zinc-400 text-xs leading-relaxed">
                                    "{analysis.transcript?.transcript?.substring(0, 1000)}..."
                                </div>
                            </div>
                        </div>

                        {/* Right Column: Deliberation Log */}
                        <div className="lg:col-span-4 h-full">
                            <div className="glass-card h-full rounded-3xl border border-zinc-800 overflow-hidden flex flex-col">
                                <div className="p-4 bg-zinc-900/50 border-b border-zinc-800 flex items-center gap-2">
                                    <Terminal size={14} className="text-emerald-500" />
                                    <span className="text-[10px] font-black text-zinc-100 uppercase tracking-widest">Agent_Deliberation_Logs</span>
                                </div>
                                <div className="flex-1 overflow-y-auto p-4 space-y-4 font-mono text-[10px]">
                                    {analysis.deliberation_log?.map((log: any, i: number) => (
                                        <div key={i} className="border-l border-zinc-800 pl-3 relative">
                                            <div className="absolute -left-[1.5px] top-0 w-1 h-1 rounded-full bg-emerald-500"></div>
                                            <div className="flex justify-between text-zinc-600 mb-1">
                                                <span>[{log.step}]</span>
                                                <span>{log.timestamp?.split('T')[1]?.substring(0, 8)}</span>
                                            </div>
                                            <p className="text-zinc-200 uppercase font-bold">{log.message}</p>
                                            {log.details && (
                                                <div className="mt-1 text-zinc-500 bg-zinc-950/50 p-2 rounded">
                                                    {JSON.stringify(log.details, null, 2)}
                                                </div>
                                            )}
                                        </div>
                                    ))}
                                </div>
                                <button
                                    onClick={() => { mutation.reset(); setVideoUrl(''); }}
                                    className="w-full py-4 text-[10px] font-black uppercase tracking-widest text-zinc-500 border-t border-zinc-800 hover:bg-zinc-900 transition-colors"
                                >
                                    NEW_SCAN_PROTOCOL
                                </button>
                            </div>
                        </div>
                    </div>
                ))
            }
        </div>
    );
};

export default HypeSlayerView;
