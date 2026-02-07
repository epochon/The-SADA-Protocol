'use client';

import React from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { ErrorBoundary } from 'react-error-boundary';

// Create a client
const queryClient = new QueryClient();

// Error Fallback
function ErrorFallback({ error, resetErrorBoundary }: { error: any; resetErrorBoundary: () => void }) {
    return (
        <div className="flex flex-col items-center justify-center p-8 text-center text-red-500 bg-red-950/20 rounded-xl border border-red-900 mx-auto my-8 max-w-lg">
            <h2 className="text-xl font-bold mb-2">Something went wrong</h2>
            <pre className="text-xs bg-black/50 p-4 rounded mb-4 overflow-auto max-w-full font-mono text-zinc-400">
                {error.message}
            </pre>
            <button
                onClick={resetErrorBoundary}
                className="px-4 py-2 bg-red-600 hover:bg-red-500 text-white rounded transition-colors"
            >
                Try again
            </button>
        </div>
    );
}

export default function Providers({ children }: { children: React.ReactNode }) {
    return (
        <ErrorBoundary FallbackComponent={ErrorFallback}>
            <QueryClientProvider client={queryClient}>
                {children}
                {process.env.NODE_ENV === 'development' && <ReactQueryDevtools initialIsOpen={false} />}
            </QueryClientProvider>
        </ErrorBoundary>
    );
}
