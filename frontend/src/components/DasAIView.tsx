'use client';

import React, { useState, useEffect, useRef, useCallback } from 'react';

// =====================================
// DAS AI VIEW - Advanced AI Interface
// =====================================

type ModelTier = 'fast' | 'balanced' | 'deep';

interface ModelOption {
  tier: ModelTier;
  label: string;
  description: string;
}

const MODEL_OPTIONS: ModelOption[] = [
  { tier: 'fast', label: 'Fast', description: 'Quick responses, lighter workloads' },
  { tier: 'balanced', label: 'Balanced', description: 'General purpose, versatile' },
  { tier: 'deep', label: 'Deep', description: 'Complex reasoning, research tasks' },
];

const DasAIView: React.FC = () => {
  const [promptValue, setPromptValue] = useState('');
  const [selectedModel, setSelectedModel] = useState<ModelTier>('fast');
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [isVoiceActive, setIsVoiceActive] = useState(false);
  const [mousePos, setMousePos] = useState({ x: 0.5, y: 0.5 });

  const containerRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Handle mouse movement for orb parallax effect
  const handleMouseMove = useCallback((e: MouseEvent) => {
    if (containerRef.current) {
      const rect = containerRef.current.getBoundingClientRect();
      const x = (e.clientX - rect.left) / rect.width;
      const y = (e.clientY - rect.top) / rect.height;
      setMousePos({ x, y });
    }
  }, []);

  useEffect(() => {
    const container = containerRef.current;
    if (container) {
      container.addEventListener('mousemove', handleMouseMove);
      return () => container.removeEventListener('mousemove', handleMouseMove);
    }
  }, [handleMouseMove]);

  // Close dropdown on outside click
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setIsDropdownOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`;
    }
  }, [promptValue]);

  const [isLoading, setIsLoading] = useState(false);
  const [loadingMessage, setLoadingMessage] = useState('');
  const [response, setResponse] = useState<any>(null);

  const handleSubmit = async () => {
    if (!promptValue.trim()) return;

    setIsLoading(true);
    setResponse(null);
    const input = promptValue.trim();
    setPromptValue(''); // Clear input immediately

    try {
      console.log('Submitting prompt:', input);

      let endpoint: string;
      let body: any;

      // Smart routing based on input type
      if (input.includes('youtube.com') || input.includes('youtu.be')) {
        // YouTube URL → Full Video Analysis Pipeline
        setLoadingMessage('📹 Fetching video transcript and analyzing...');
        endpoint = 'http://localhost:8000/hypeslayer/analyze-video';
        body = { video_url: input };
      } else {
        // Text claim → Cross-Verification Pipeline
        setLoadingMessage('🔍 Cross-verifying claim against multiple sources...');
        endpoint = 'http://localhost:8000/hypeslayer/cross-verify';
        body = { transcript: input };
      }

      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      });

      if (!res.ok) {
        const errorText = await res.text();
        throw new Error(`API Error ${res.status}: ${errorText}`);
      }

      const data = await res.json();
      console.log('Full Response:', data);
      setResponse(data);

    } catch (error: any) {
      console.error('Error submitting prompt:', error);
      setResponse({
        decision: 'ERROR',
        confidence_score: 0,
        entities: { claim: input },
        reason: error.message || 'Failed to connect to backend',
        error_details: 'Please ensure backend is running at http://localhost:8000'
      });
    } finally {
      setIsLoading(false);
      setLoadingMessage('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleFileUpload = () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.multiple = true;
    input.accept = 'image/*,.pdf,.csv,.json,.txt,.doc,.docx,.xls,.xlsx';
    input.onchange = (e) => {
      const files = (e.target as HTMLInputElement).files;
      if (files) {
        console.log('Files selected:', Array.from(files).map(f => f.name));
        // TODO: Handle file upload
      }
    };
    input.click();
  };

  const toggleVoice = () => {
    setIsVoiceActive(!isVoiceActive);
    // TODO: Implement voice recording
  };

  // Calculate orb transform based on mouse position
  const orbTransform = {
    transform: `translate(-50%, -50%) translate3d(${(mousePos.x - 0.5) * 20}px, ${(mousePos.y - 0.5) * 20}px, 0)`,
  };

  return (
    <div
      ref={containerRef}
      className="relative w-full h-full min-h-[600px] overflow-hidden"
      style={{ background: 'radial-gradient(ellipse at center, #0a0a0a 0%, #000000 100%)' }}
    >
      {/* CSS Keyframes */}
      <style jsx>{`
        @keyframes pulse-glow {
          0%, 100% { opacity: 0.3; transform: translate(-50%, -50%) scale(1); }
          50% { opacity: 0.5; transform: translate(-50%, -50%) scale(1.1); }
        }
        @keyframes ripple-pulse {
          0%, 100% { opacity: 1; transform: translate(-50%, -50%) scale(1); }
          50% { opacity: 0.6; transform: translate(-50%, -50%) scale(1.05); }
        }
        @keyframes orb-float {
          0%, 100% { transform: translate(-50%, -50%) translateY(0px); }
          50% { transform: translate(-50%, -50%) translateY(-10px); }
        }
        @keyframes shimmer {
          0% { opacity: 0.4; }
          50% { opacity: 0.8; }
          100% { opacity: 0.4; }
        }
        @keyframes pulse-ring {
          0%, 100% { transform: translate(-50%, -50%) scale(1); opacity: 1; }
          50% { transform: translate(-50%, -50%) scale(1.3); opacity: 0; }
        }
        .orb-glow {
          animation: pulse-glow 4s ease-in-out infinite;
        }
        .orb-core {
          animation: orb-float 6s ease-in-out infinite;
        }
        .orb-inner-glow {
          animation: shimmer 3s ease-in-out infinite;
        }
        .ripple-ring {
          animation: ripple-pulse 3s ease-in-out infinite;
        }
        .ripple-ring[data-layer="1"] { animation-delay: 0s; }
        .ripple-ring[data-layer="2"] { animation-delay: 0.6s; }
        .ripple-ring[data-layer="3"] { animation-delay: 1.2s; }
        .ripple-ring[data-layer="4"] { animation-delay: 1.8s; }
        .ripple-ring[data-layer="5"] { animation-delay: 2.4s; }
        .voice-pulse {
          animation: pulse-ring 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
        }
      `}</style>

      {/* Logo & Branding */}
      <header className="absolute top-10 left-10 z-50 select-none">
        <h1 className="text-5xl font-bold text-white tracking-tight mb-2">Das AI</h1>
        <p className="text-[11px] text-white/70 tracking-wide leading-relaxed max-w-[200px]">
          by DAS THE HYPESLAYER<br />
          Advanced AI reasoning<br />
          with deep research, coding<br />
          capabilities and enhanced<br />
          financial decision-making.
        </p>
      </header>

      {/* Central Orb Visualization - Fixed positioned like reference */}
      <div
        className={`fixed top-1/2 left-1/2 w-[400px] h-[400px] pointer-events-none z-[1] transition-opacity duration-500 ${response ? 'opacity-20 blur-md' : 'opacity-100'}`}
        style={{ transform: 'translate(-50%, -50%)' }}
      >
        {/* Outer Glow Layer */}
        <div
          className="orb-glow absolute top-1/2 left-1/2 w-[300px] h-[300px] rounded-full"
          style={{
            transform: 'translate(-50%, -50%)',
            background: 'radial-gradient(circle, rgba(255, 255, 255, 0.3) 0%, transparent 70%)',
            filter: 'blur(60px)',
            opacity: 0.4,
          }}
        />

        {/* Ripple Ring System */}
        <div
          className="absolute top-1/2 left-1/2 w-full h-full"
          style={{ transform: 'translate(-50%, -50%)' }}
        >
          {/* Layer 1 - Outermost */}
          <div
            data-layer="1"
            className="ripple-ring absolute top-1/2 left-1/2 rounded-full border-2"
            style={{
              transform: 'translate(-50%, -50%)',
              width: '360px',
              height: '360px',
              borderColor: 'rgba(91, 200, 232, 0.15)',
            }}
          />
          {/* Layer 2 */}
          <div
            data-layer="2"
            className="ripple-ring absolute top-1/2 left-1/2 rounded-full border-2"
            style={{
              transform: 'translate(-50%, -50%)',
              width: '320px',
              height: '320px',
              borderColor: 'rgba(59, 166, 201, 0.25)',
            }}
          />
          {/* Layer 3 */}
          <div
            data-layer="3"
            className="ripple-ring absolute top-1/2 left-1/2 rounded-full border-2"
            style={{
              transform: 'translate(-50%, -50%)',
              width: '280px',
              height: '280px',
              borderColor: 'rgba(0, 212, 255, 0.35)',
            }}
          />
          {/* Layer 4 */}
          <div
            data-layer="4"
            className="ripple-ring absolute top-1/2 left-1/2 rounded-full border-2"
            style={{
              transform: 'translate(-50%, -50%)',
              width: '240px',
              height: '240px',
              borderColor: 'rgba(91, 200, 232, 0.45)',
            }}
          />
          {/* Layer 5 - Innermost */}
          <div
            data-layer="5"
            className="ripple-ring absolute top-1/2 left-1/2 rounded-full border-2"
            style={{
              transform: 'translate(-50%, -50%)',
              width: '200px',
              height: '200px',
              borderColor: 'rgba(0, 212, 255, 0.55)',
            }}
          />
        </div>

        {/* Core Luminous Sphere */}
        <div
          className="orb-core absolute top-1/2 left-1/2 w-40 h-40 rounded-full"
          style={{
            transform: 'translate(-50%, -50%) translateZ(0)',
            background: 'radial-gradient(circle at 40% 40%, #FFFFFF 0%, #00D4FF 30%, #3BA6C9 60%, rgba(0, 212, 255, 0.4) 90%, transparent 100%)',
            boxShadow: '0 0 40px rgba(0, 212, 255, 0.8), 0 0 80px rgba(0, 212, 255, 0.4), inset 0 0 20px rgba(255, 255, 255, 0.5)',
            backfaceVisibility: 'hidden',
            perspective: '1000px',
          }}
        >
          <div
            className="orb-inner-glow absolute inset-[10%] rounded-full"
            style={{
              background: 'radial-gradient(circle at 30% 30%, rgba(255, 255, 255, 0.8) 0%, transparent 60%)',
            }}
          />
        </div>

        {/* Watermark Text */}
        {!response && !isLoading && (
          <div
            className="absolute top-1/2 left-1/2 text-[120px] font-black text-white/[0.08] tracking-widest z-[5] pointer-events-none select-none"
            style={{
              transform: 'translate(-50%, -50%)',
              mixBlendMode: 'overlay',
            }}
          >
            AI AT WORK
          </div>
        )}
      </div>

      {/* Response Overlay */}
      {(response || isLoading) && (
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-[55%] w-[700px] max-w-[95vw] max-h-[80vh] overflow-y-auto z-40 scrollbar-thin scrollbar-thumb-cyan-500/30 scrollbar-track-transparent">
          {isLoading ? (
            <div className="flex flex-col items-center justify-center animate-pulse py-10">
              <div className="w-16 h-16 border-4 border-cyan-400/30 border-t-cyan-400 rounded-full animate-spin mb-4"></div>
              <div className="text-cyan-400 text-xl font-mono mb-2">ANALYZING...</div>
              <div className="text-white/60 text-sm text-center max-w-md">{loadingMessage || 'Cross-referencing market data, news, and sentiment'}</div>
            </div>
          ) : (
            <div className="bg-black/90 backdrop-blur-xl border border-cyan-500/40 rounded-2xl p-6 shadow-[0_0_60px_rgba(0,212,255,0.2)]">
              {/* Header: Decision + Confidence */}
              <div className="flex justify-between items-center mb-6 pb-4 border-b border-white/10">
                <div className="flex items-center gap-3">
                  <div className={`w-4 h-4 rounded-full ${response.decision === 'VERIFY' ? 'bg-green-500' : response.decision === 'REFUSE' ? 'bg-red-500' : 'bg-yellow-500'} animate-pulse`}></div>
                  <h2 className={`text-3xl font-black tracking-tight ${response.decision === 'VERIFY' ? 'text-green-400' : response.decision === 'REFUSE' ? 'text-red-400' : 'text-yellow-400'}`}>
                    {response.decision || 'ANALYSIS COMPLETE'}
                  </h2>
                </div>
                <div className="text-right">
                  <div className="text-white/50 text-xs uppercase tracking-widest mb-1">Confidence</div>
                  <div className="text-2xl font-mono font-bold text-white">{response.confidence_score || response.confidence?.confidence_score || 0}%</div>
                </div>
              </div>

              <div className="space-y-5 text-white/90">
                {/* Main Reason / Summary */}
                {(response.reason || response.confidence?.reasoning) && (
                  <div className="bg-gradient-to-r from-cyan-500/10 to-transparent p-4 rounded-xl border-l-4 border-cyan-500">
                    <div className="text-xs text-cyan-400 uppercase tracking-widest mb-2 font-semibold">📋 Analysis Summary</div>
                    <div className="text-lg leading-relaxed">{response.reason || response.confidence?.reasoning}</div>
                  </div>
                )}

                {/* Entities Extracted */}
                {response.entities && (
                  <div className="bg-white/5 p-4 rounded-xl border border-white/10">
                    <div className="text-xs text-purple-400 uppercase tracking-widest mb-3 font-semibold">🎯 Extracted Entities</div>
                    <div className="grid grid-cols-2 gap-3 text-sm">
                      {response.entities.asset && (
                        <div className="bg-purple-500/10 p-3 rounded-lg border border-purple-500/20">
                          <span className="text-white/50 block text-xs mb-1">Asset</span>
                          <span className="font-bold text-purple-300">{response.entities.asset.ticker || response.entities.asset}</span>
                          {response.entities.asset.type && <span className="text-white/40 text-xs ml-2">({response.entities.asset.type})</span>}
                        </div>
                      )}
                      {response.entities.claim && (
                        <div className="col-span-2 bg-white/5 p-3 rounded-lg border border-white/5">
                          <span className="text-white/50 block text-xs mb-1">Claimed</span>
                          <span className="italic text-white/80">"{response.entities.claim}"</span>
                        </div>
                      )}
                      {response.entities.timeline && (
                        <div className="bg-blue-500/10 p-3 rounded-lg border border-blue-500/20">
                          <span className="text-white/50 block text-xs mb-1">Timeline</span>
                          <span className="text-blue-300">{response.entities.timeline}</span>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* Verification Results */}
                {response.verification && (
                  <div className="bg-white/5 p-4 rounded-xl border border-white/10">
                    <div className="text-xs text-green-400 uppercase tracking-widest mb-3 font-semibold">✅ Fact Check Results</div>
                    <div className="grid grid-cols-2 gap-3 text-sm">
                      {response.verification.real_data && (
                        <>
                          {response.verification.real_data.current_price && (
                            <div className="p-3 bg-green-500/10 rounded-lg border border-green-500/20">
                              <span className="text-white/50 block text-xs mb-1">Current Price</span>
                              <span className="font-bold text-green-300 text-lg">${response.verification.real_data.current_price}</span>
                            </div>
                          )}
                          {response.verification.real_data.recommendation && (
                            <div className="p-3 bg-green-500/10 rounded-lg border border-green-500/20">
                              <span className="text-white/50 block text-xs mb-1">Analyst Rating</span>
                              <span className="font-semibold text-green-300 uppercase">{response.verification.real_data.recommendation}</span>
                            </div>
                          )}
                          {response.verification.real_data.target_mean_price && (
                            <div className="p-3 bg-white/5 rounded-lg">
                              <span className="text-white/50 block text-xs mb-1">Target Price</span>
                              <span className="text-white/80">${response.verification.real_data.target_mean_price}</span>
                            </div>
                          )}
                          {response.verification.real_data.pe_ratio && (
                            <div className="p-3 bg-white/5 rounded-lg">
                              <span className="text-white/50 block text-xs mb-1">P/E Ratio</span>
                              <span className="text-white/80">{response.verification.real_data.pe_ratio.toFixed(2)}</span>
                            </div>
                          )}
                        </>
                      )}
                      <div className="col-span-2 flex items-center gap-2 mt-2">
                        <span className="text-white/50 text-xs">Discrepancy Score:</span>
                        <div className="flex-1 h-2 bg-white/10 rounded-full overflow-hidden">
                          <div
                            className={`h-full rounded-full ${(response.verification.discrepancy_score || 0) > 50 ? 'bg-red-500' : 'bg-green-500'}`}
                            style={{ width: `${response.verification.discrepancy_score || 0}%` }}
                          ></div>
                        </div>
                        <span className="text-white/70 text-sm font-mono">{response.verification.discrepancy_score || 0}%</span>
                      </div>
                    </div>
                  </div>
                )}

                {/* Sentiment Analysis */}
                {response.sentiment && (
                  <div className="bg-white/5 p-4 rounded-xl border border-white/10">
                    <div className="text-xs text-orange-400 uppercase tracking-widest mb-3 font-semibold">🔥 Hype Analysis</div>
                    <div className="flex items-center gap-4">
                      <div className={`px-4 py-2 rounded-full font-bold text-sm ${response.sentiment.hype_level === 'EXTREME' ? 'bg-red-500/30 text-red-300 border border-red-500/50' :
                        response.sentiment.hype_level === 'HIGH' ? 'bg-orange-500/30 text-orange-300 border border-orange-500/50' :
                          response.sentiment.hype_level === 'MEDIUM' ? 'bg-yellow-500/30 text-yellow-300 border border-yellow-500/50' :
                            'bg-green-500/30 text-green-300 border border-green-500/50'
                        }`}>
                        {response.sentiment.hype_level} HYPE
                      </div>
                      <div className="text-white/60 text-sm">
                        Penalty: <span className="text-orange-400 font-mono">-{response.sentiment.hype_penalty || 0}</span> points
                      </div>
                    </div>
                  </div>
                )}

                {/* Transcript Info (for video analysis) */}
                {response.transcript && response.transcript.word_count && (
                  <div className="bg-white/5 p-4 rounded-xl border border-white/10">
                    <div className="text-xs text-blue-400 uppercase tracking-widest mb-2 font-semibold">📹 Video Transcript</div>
                    <div className="text-sm text-white/60">
                      Analyzed <span className="text-white font-semibold">{response.transcript.word_count}</span> words from video
                      {response.transcript.video_id && <span className="ml-2 text-white/40">(ID: {response.transcript.video_id})</span>}
                    </div>
                  </div>
                )}

                {/* Error Details */}
                {response.error_details && (
                  <div className="bg-red-500/10 p-4 rounded-xl border border-red-500/30">
                    <div className="text-xs text-red-400 uppercase tracking-widest mb-2 font-semibold">⚠️ Error</div>
                    <div className="text-red-300 text-sm">{response.error_details}</div>
                  </div>
                )}

                {/* Deliberation Log (Collapsible) */}
                {response.deliberation_log && response.deliberation_log.length > 0 && (
                  <details className="bg-white/5 rounded-xl border border-white/10">
                    <summary className="p-4 cursor-pointer text-xs text-white/50 uppercase tracking-widest hover:text-white/80 transition-colors">
                      🔬 View Deliberation Process ({response.deliberation_log.length} steps)
                    </summary>
                    <div className="px-4 pb-4 space-y-2">
                      {response.deliberation_log.map((step: any, idx: number) => (
                        <div key={idx} className="flex items-start gap-3 text-xs">
                          <div className={`w-2 h-2 rounded-full mt-1.5 ${step.status === 'complete' ? 'bg-green-500' : 'bg-yellow-500'}`}></div>
                          <div>
                            <span className="text-cyan-400 font-semibold">{step.step}:</span>
                            <span className="text-white/70 ml-2">{step.message}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </details>
                )}
              </div>

              <button
                onClick={() => setResponse(null)}
                className="mt-6 w-full py-3 bg-cyan-500/10 hover:bg-cyan-500/20 border border-cyan-500/30 hover:border-cyan-500/60 rounded-xl text-cyan-400 hover:text-cyan-300 transition-all text-sm font-semibold uppercase tracking-widest"
              >
                ✕ Close Analysis
              </button>
            </div>
          )}
        </div>
      )}

      {/* Interactive Prompt Container */}
      <section className="absolute bottom-10 left-1/2 -translate-x-1/2 w-[720px] max-w-[90vw] z-50">
        <div
          className="relative backdrop-blur-xl border border-white/10 rounded-3xl px-5 py-4 transition-all duration-300 focus-within:border-cyan-400/50 focus-within:shadow-[0_0_0_1px_rgba(0,212,255,0.2)]"
          style={{
            background: 'rgba(20, 20, 20, 0.95)',
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.5)',
          }}
        >
          <div className="flex items-center gap-3">
            {/* File Upload Button */}
            <button
              onClick={handleFileUpload}
              className="w-10 h-10 min-w-[40px] rounded-full bg-white/5 border border-white/10 text-white/70 flex items-center justify-center transition-all hover:bg-cyan-400/10 hover:border-cyan-400/40 hover:text-cyan-400 hover:scale-105 active:scale-95"
              aria-label="Upload file"
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                <path d="M12 5V19M5 12H19" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </button>

            {/* Main Input Area */}
            <div className="flex-1">
              <textarea
                ref={textareaRef}
                value={promptValue}
                onChange={(e) => setPromptValue(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask anything or upload a file..."
                rows={1}
                className="w-full bg-transparent border-none outline-none text-white text-base resize-none max-h-[200px] leading-normal py-1 placeholder:text-white/40"
                spellCheck="true"
              />
            </div>

            {/* Voice Input Button */}
            <button
              onClick={toggleVoice}
              className={`relative w-12 h-12 min-w-[48px] rounded-full border flex items-center justify-center transition-all duration-300 ${isVoiceActive
                ? 'bg-cyan-400/20 border-cyan-400 text-cyan-400'
                : 'bg-white/5 border-white/10 text-white/70 hover:bg-cyan-400/10 hover:border-cyan-400/30 hover:text-cyan-400'
                }`}
              aria-label="Voice input"
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                <rect x="9" y="2" width="6" height="12" rx="3" stroke="currentColor" strokeWidth="2" />
                <path d="M5 10V12C5 15.866 8.134 19 12 19C15.866 19 19 15.866 19 12V10" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                <path d="M12 19V22M8 22H16" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
              </svg>
              {isVoiceActive && (
                <span className="voice-pulse absolute inset-0 rounded-full border-2 border-cyan-400 pointer-events-none" />
              )}
            </button>

            {/* Model Selection Dropdown */}
            <div ref={dropdownRef} className="relative">
              <button
                onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                className="flex items-center gap-2 px-4 py-2 bg-white/5 border border-white/10 rounded-2xl text-white text-sm whitespace-nowrap transition-all hover:bg-white/10 hover:border-cyan-400/30"
                aria-label="Select AI model"
                aria-expanded={isDropdownOpen}
              >
                <span className="font-medium">
                  {MODEL_OPTIONS.find(m => m.tier === selectedModel)?.label}
                </span>
                <svg
                  className={`w-4 h-4 transition-transform ${isDropdownOpen ? 'rotate-180' : ''}`}
                  viewBox="0 0 16 16"
                  fill="none"
                >
                  <path d="M4 6L8 10L12 6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              </button>

              {/* Dropdown Menu */}
              {isDropdownOpen && (
                <div
                  className="absolute bottom-full right-0 mb-2 min-w-[280px] backdrop-blur-xl border border-white/10 rounded-lg p-2 z-50"
                  style={{
                    background: 'rgba(20, 20, 20, 0.95)',
                    boxShadow: '0 16px 64px rgba(0, 0, 0, 0.6)',
                  }}
                >
                  {MODEL_OPTIONS.map((option) => (
                    <div
                      key={option.tier}
                      onClick={() => {
                        setSelectedModel(option.tier);
                        setIsDropdownOpen(false);
                      }}
                      className={`px-4 py-3 rounded-lg cursor-pointer transition-colors ${selectedModel === option.tier ? 'bg-cyan-400/15' : 'hover:bg-cyan-400/10'
                        }`}
                    >
                      <div className="text-white font-semibold text-sm mb-1">{option.label}</div>
                      <div className="text-white/60 text-xs leading-relaxed">{option.description}</div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default DasAIView;
