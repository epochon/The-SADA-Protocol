'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Loader2 } from 'lucide-react';

interface ComponentProps { }

// Define message type
type Message = {
    role: 'assistant' | 'user';
    content: string;
};

const ChatInterface: React.FC<ComponentProps> = () => {
    const [messages, setMessages] = useState<Message[]>([
        {
            role: 'assistant',
            content: "Hello! I'm SADA, your AI financial advisor. I can help analyze markets, manage your portfolio, or answer financial questions. How can I assist you today?"
        }
    ]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const sendMessage = async () => {
        if (!input.trim()) return;

        const userMsg: Message = { role: 'user', content: input };
        setMessages(prev => [...prev, userMsg]);
        setInput('');
        setIsLoading(true);

        try {
            // Direct call to backend
            const res = await fetch('/api/agent/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    messages: [...messages, userMsg],
                    model: 'gpt-4-turbo' // Optional
                }),
            });

            if (!res.ok) throw new Error('Failed to get response');

            const data = await res.json();
            // Expecting { role: 'assistant', content: '...' }
            // The backend returns directly { role: "assistant", content: response }?
            // Check backend agent.py: return {"role": "assistant", "content": response}
            // Yes.

            // Wait, backend response structure:
            // return {"role": "assistant", "content": response} -> Object
            // data is { role: ..., content: ... }

            // Some APIs return nested structure. My backend is flat.

            const assistantMsg: Message = {
                role: 'assistant',
                content: data.content || "I'm having trouble connecting right now."
            };

            setMessages(prev => [...prev, assistantMsg]);
        } catch (error) {
            console.error('Chat error:', error);
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: "Sorry, I encountered an error connecting to the server. Please check your connection."
            }]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    };

    return (
        <div className="glass-card h-full rounded-xl flex flex-col p-4 relative overflow-hidden">
            <div className="flex items-center justify-between mb-4 border-b border-zinc-800 pb-2">
                <div className="flex items-center space-x-2">
                    <div className="w-8 h-8 rounded-full bg-emerald-500/10 flex items-center justify-center text-emerald-400">
                        <Bot size={18} />
                    </div>
                    <h2 className="font-semibold text-zinc-100">Financial Advisor</h2>
                </div>
                <span className="text-xs px-2 py-1 bg-emerald-500/10 text-emerald-400 rounded-full border border-emerald-500/20 flex items-center">
                    <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full mr-1.5 animate-pulse"></span>
                    Online
                </span>
            </div>

            <div className="flex-1 overflow-y-auto mb-4 custom-scrollbar space-y-4 pr-2">
                {messages.map((msg, index) => (
                    <div
                        key={index}
                        className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                        <div
                            className={`max-w-[85%] rounded-lg p-3 text-sm ${msg.role === 'user'
                                    ? 'bg-emerald-600/20 text-emerald-50 border border-emerald-500/30'
                                    : 'bg-zinc-800/50 text-zinc-200 border border-zinc-700/50'
                                }`}
                        >
                            {msg.content}
                        </div>
                    </div>
                ))}
                {isLoading && (
                    <div className="flex justify-start">
                        <div className="bg-zinc-800/50 rounded-lg p-3 border border-zinc-700/50 flex items-center space-x-2">
                            <Loader2 size={16} className="animate-spin text-emerald-400" />
                            <span className="text-xs text-zinc-400">Analyzing...</span>
                        </div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            <div className="relative mt-auto">
                <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder="Ask SADA for advice..."
                    disabled={isLoading}
                    className="w-full bg-zinc-900 border border-zinc-700 rounded-lg py-3 pl-4 pr-12 text-sm text-zinc-100 focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 transition-all placeholder-zinc-500 disabled:opacity-50"
                />
                <button
                    onClick={sendMessage}
                    disabled={!input.trim() || isLoading}
                    className="absolute right-2 top-1/2 transform -translate-y-1/2 p-1.5 text-zinc-400 hover:text-emerald-400 disabled:text-zinc-600 transition-colors"
                >
                    <Send size={18} />
                </button>
            </div>
        </div>
    );
};

export default ChatInterface;
