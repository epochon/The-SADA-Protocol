# 🛡️ HypeSlayer API Documentation

**Financial Reality Check Agent - Backend API Reference**

Base URL: `http://localhost:8000`

---

## 📋 Table of Contents
1. [Authentication](#authentication)
2. [Video Processing](#video-processing)
3. [Entity Extraction](#entity-extraction)
4. [Fact Verification](#fact-verification)
5. [Sentiment Analysis](#sentiment-analysis)
6. [Decision Making](#decision-making)
7. [Bullshit Detection](#bullshit-detection)
8. [Health Check](#health-check)
9. [Error Handling](#error-handling)
10. [Example Workflows](#example-workflows)

---

## 🔐 Authentication

Currently, no authentication is required. All endpoints are open for development.

**CORS**: Enabled for `http://localhost:3000` (Frontend)

---

## 📹 Video Processing

### 1. Ingest YouTube Video

Extract transcript from a YouTube video.

**Endpoint:** `POST /hypeslayer/ingest-video`

**Request Body:**
```json
{
  "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
}
```

**Response:**
```json
{
  "transcript": "Full video transcript text...",
  "video_id": "dQw4w9WgXcQ",
  "status": "success"
}
```

**Error Responses:**
- `400`: Invalid YouTube URL
- `500`: Failed to fetch transcript (video may not have captions)

**Example cURL:**
```bash
curl -X POST "http://localhost:8000/hypeslayer/ingest-video" \
  -H "Content-Type: application/json" \
  -d '{"video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}'
```

---

## 🧠 Entity Extraction

### 2. Parse Financial Entities

Extract ticker, claims, and timeline from transcript using Groq LLM.

**Endpoint:** `POST /hypeslayer/parse-entities`

**Request Body:**
```json
{
  "transcript": "I think GameStop stock (GME) will hit $500 by next month!"
}
```

**Response:**
```json
{
  "asset_type": "stock",
  "ticker": "GME",
  "claim": "Price will hit $500",
  "timeline": "By next month",
  "confidence": 0.85,
  "refusal_reason": null
}
```

**Epistemic Refusal Example:**
```json
{
  "asset_type": "unknown",
  "ticker": null,
  "claim": null,
  "timeline": null,
  "confidence": 0.0,
  "refusal_reason": "No clear ticker symbol identified"
}
```

**Example cURL:**
```bash
curl -X POST "http://localhost:8000/hypeslayer/parse-entities" \
  -H "Content-Type: application/json" \
  -d '{"transcript": "GME is going to the moon! 🚀"}'
```

---

## ✅ Fact Verification

### 3. Verify Financial Claim

Compare claims against real market data from yfinance.

**Endpoint:** `POST /hypeslayer/verify-claim`

**Request Body:**
```json
{
  "ticker": "GME",
  "claim": "Revenue is skyrocketing",
  "claim_type": "revenue"
}
```

**Response:**
```json
{
  "verification_status": "verified",
  "real_data": {
    "current_price": 23.45,
    "market_cap": 9500000000,
    "pe_ratio": 15.2,
    "revenue": 6500000000
  },
  "discrepancy_score": 0,
  "evidence_quality": 0.7
}
```

**Failed Verification Example:**
```json
{
  "verification_status": "failed",
  "real_data": {},
  "discrepancy_score": 100,
  "evidence_quality": 0.0,
  "error": "Invalid ticker symbol"
}
```

**Example cURL:**
```bash
curl -X POST "http://localhost:8000/hypeslayer/verify-claim" \
  -H "Content-Type: application/json" \
  -d '{"ticker": "AAPL", "claim": "Revenue is growing", "claim_type": "revenue"}'
```

---

## 😱 Sentiment Analysis

### 4. Analyze Hype Level

Detect emotional hype using VADER sentiment analysis.

**Endpoint:** `POST /hypeslayer/analyze-sentiment`

**Request Body:**
```json
{
  "text": "This stock is AMAZING! To the MOON! 🚀🚀🚀"
}
```

**Response:**
```json
{
  "sentiment_score": 0.92,
  "hype_level": "EXTREME",
  "hype_penalty": 35,
  "emotional_intensity": "high"
}
```

**Hype Levels:**
- `EXTREME` (score > 0.8): Penalty = 35
- `HIGH` (score > 0.5): Penalty = 25
- `MODERATE` (score > 0.2): Penalty = 10
- `LOW` (score ≤ 0.2): Penalty = 0

**Example cURL:**
```bash
curl -X POST "http://localhost:8000/hypeslayer/analyze-sentiment" \
  -H "Content-Type: application/json" \
  -d '{"text": "GME is going to the MOON! 🚀🚀🚀"}'
```

---

## 🎯 Decision Making

### 5. Calculate Confidence Score

Determine whether to REFUSE or VERIFY based on confidence formula.

**Endpoint:** `POST /hypeslayer/calculate-confidence`

**Request Body:**
```json
{
  "evidence_quality": 0.7,
  "data_completeness": 0.8,
  "risk_penalty": 35,
  "hype_penalty": 25
}
```

**Response:**
```json
{
  "confidence_score": 90.0,
  "decision": "VERIFY",
  "threshold": 50,
  "reasoning": ["All checks passed"]
}
```

**Refusal Example:**
```json
{
  "confidence_score": 42.0,
  "decision": "REFUSE",
  "threshold": 50,
  "reasoning": [
    "Low evidence quality detected",
    "High emotional hype detected",
    "Confidence score (42.0) below threshold (50)"
  ]
}
```

**Formula:**
```
Score = (Evidence_Quality × 100 + Data_Completeness × 100) - (Risk_Penalty + Hype_Penalty)
Decision = VERIFY if Score ≥ 50, else REFUSE
```

**Example cURL:**
```bash
curl -X POST "http://localhost:8000/hypeslayer/calculate-confidence" \
  -H "Content-Type: application/json" \
  -d '{"evidence_quality": 0.7, "data_completeness": 0.8, "risk_penalty": 10, "hype_penalty": 15}'
```

---

## 🔗 Chain of Verification (CoVe)

### 6. Generate Verification Questions

Create fact-checking questions using Groq LLM and answer with market data.

**Endpoint:** `POST /hypeslayer/verify-chain?claim=...&ticker=...`

**Query Parameters:**
- `claim` (string): The financial claim to verify
- `ticker` (string): Stock ticker symbol

**Example Request:**
```
POST /hypeslayer/verify-chain?claim=GME revenue is growing&ticker=GME
```

**Response:**
```json
{
  "verification_questions": [
    "What is the current P/E ratio of GME?",
    "What was GME's Q3 revenue?",
    "What is the analyst consensus rating for GME?"
  ],
  "answers": [
    "Current price: $23.45",
    "Revenue: $6500000000",
    "Data not available"
  ],
  "discrepancies": []
}
```

**Example cURL:**
```bash
curl -X POST "http://localhost:8000/hypeslayer/verify-chain?claim=TSLA%20is%20undervalued&ticker=TSLA"
```

---

## 💩 Bullshit Detection

### 7. Calculate Bullshit Score

Deterministic rule-based scam detection (no LLM).

**Endpoint:** `POST /hypeslayer/bullshit-score`

**Request Body:**
```json
{
  "ticker": "SCAMCOIN",
  "data_availability": false
}
```

**Response:**
```json
{
  "bullshit_score": 100,
  "reason": "No market data available for this ticker",
  "auto_refuse": true
}
```

**Legitimate Ticker Example:**
```json
{
  "bullshit_score": 0,
  "reason": "Ticker appears legitimate",
  "auto_refuse": false
}
```

**Scoring Rules:**
- No market data = 100 (auto-refuse)
- Unknown ticker = +80
- Price deviation > 1000% = +50

**Example cURL:**
```bash
curl -X POST "http://localhost:8000/hypeslayer/bullshit-score" \
  -H "Content-Type: application/json" \
  -d '{"ticker": "AAPL", "data_availability": true}'
```

---

## 🏥 Health Check

### 8. Service Health Status

Check if all backend services are operational.

**Endpoint:** `GET /hypeslayer/health`

**Response:**
```json
{
  "status": "ok",
  "services": {
    "yfinance": "ok",
    "groq": "ok",
    "vader": "ok"
  }
}
```

**Example cURL:**
```bash
curl "http://localhost:8000/hypeslayer/health"
```

---

## ⚠️ Error Handling

All endpoints return consistent error formats:

**Standard Error Response:**
```json
{
  "detail": "Error message describing what went wrong"
}
```

**Common HTTP Status Codes:**
- `200`: Success
- `400`: Bad Request (invalid input)
- `404`: Not Found
- `500`: Internal Server Error

---

## 🔄 Example Workflows

### Complete Video Analysis Pipeline

```javascript
// Step 1: Ingest Video
const transcript = await fetch('http://localhost:8000/hypeslayer/ingest-video', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ video_url: 'https://youtube.com/watch?v=...' })
}).then(r => r.json());

// Step 2: Extract Entities
const entities = await fetch('http://localhost:8000/hypeslayer/parse-entities', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ transcript: transcript.transcript })
}).then(r => r.json());

// Step 3: Analyze Sentiment
const sentiment = await fetch('http://localhost:8000/hypeslayer/analyze-sentiment', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ text: transcript.transcript })
}).then(r => r.json());

// Step 4: Verify Claim
const verification = await fetch('http://localhost:8000/hypeslayer/verify-claim', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    ticker: entities.ticker,
    claim: entities.claim,
    claim_type: 'general'
  })
}).then(r => r.json());

// Step 5: Calculate Confidence
const decision = await fetch('http://localhost:8000/hypeslayer/calculate-confidence', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    evidence_quality: verification.evidence_quality,
    data_completeness: 0.8,
    risk_penalty: 10,
    hype_penalty: sentiment.hype_penalty
  })
}).then(r => r.json());

console.log('Final Decision:', decision.decision); // "REFUSE" or "VERIFY"
```

---

## 🚀 Interactive API Docs

Visit **`http://localhost:8000/docs`** for Swagger UI with:
- Live API testing
- Request/response schemas
- Try-it-out functionality

---

## 📞 Support

For issues or questions, contact the backend team or check the main README.

**Tech Stack:**
- FastAPI (Python)
- Groq (Llama 3.3 70B)
- yfinance
- VADER Sentiment
- YouTube Transcript API
