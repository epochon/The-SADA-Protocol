import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

export async function POST(request: NextRequest) {
    try {
        const body = await request.json();

        const response = await fetch(`${BACKEND_URL}/hypeslayer/analyze-video`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(body),
        });

        if (!response.ok) {
            const errorText = await response.text();
            return NextResponse.json(
                {
                    decision: 'REFUSE',
                    confidence_score: 0,
                    reason: `Backend error: ${response.status} - ${errorText}`,
                    deliberation_log: [{
                        step: 'API_ERROR',
                        status: 'failed',
                        message: `Backend returned ${response.status}`,
                        timestamp: new Date().toISOString()
                    }]
                },
                { status: response.status }
            );
        }

        const data = await response.json();
        return NextResponse.json(data);

    } catch (error: any) {
        console.error('API Proxy Error:', error);
        return NextResponse.json(
            {
                decision: 'REFUSE',
                confidence_score: 0,
                reason: `Failed to connect to backend: ${error.message}`,
                deliberation_log: [{
                    step: 'CONNECTION_ERROR',
                    status: 'failed',
                    message: 'Backend server unreachable. Ensure backend is running at http://localhost:8000',
                    timestamp: new Date().toISOString()
                }]
            },
            { status: 500 }
        );
    }
}
