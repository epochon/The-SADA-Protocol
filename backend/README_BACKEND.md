# DAS AI - HypeSlayer Backend

Financial Reality Check Agent API

## Quick Start

```bash
cd backend
python -m venv venv
.\venv\Scripts\activate  # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## API Endpoints

### Core Analysis Pipeline

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/analyze-video` | POST | **Main endpoint** - Full video analysis pipeline |
| `/api/health` | GET | Service health check |

### Individual Services

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/ingest-video` | POST | Fetch YouTube transcript |
| `/api/parse-entities` | POST | Extract ticker, claim, timeline |
| `/api/verify-claim` | POST | Verify claim vs yfinance data |
| `/api/analyze-sentiment` | POST | VADER sentiment + hype detection |
| `/api/calculate-confidence` | POST | Calculate confidence score |
| `/api/verify-chain` | POST | Chain of Verification questions |
| `/api/bullshit-score` | POST | Deterministic scam detection |

---

## Example Requests

### Full Video Analysis
```bash
curl -X POST http://localhost:8000/api/analyze-video \
  -H "Content-Type: application/json" \
  -d '{"video_url": "https://youtube.com/watch?v=VIDEO_ID"}'
```

### Response Format
```json
{
  "decision": "REFUSE" | "VERIFY",
  "confidence_score": 42.5,
  "transcript": {...},
  "entities": {"asset": {"ticker": "GME"}, "claim": "..."},
  "verification": {"discrepancy_score": 65, ...},
  "sentiment": {"hype_level": "HIGH", "hype_penalty": 35},
  "deliberation_log": [...]
}
```

### Sentiment Analysis
```bash
curl -X POST http://localhost:8000/api/analyze-sentiment \
  -H "Content-Type: application/json" \
  -d '{"text": "This stock is going TO THE MOON! 🚀 Guaranteed 100x gains!"}'
```

### Bullshit Score
```bash
curl -X POST http://localhost:8000/api/bullshit-score \
  -H "Content-Type: application/json" \
  -d '{"ticker": "FAKECOIN", "claimed_price": 10000}'
```

---

## Environment Variables

Create `.env` file:
```
OPENAI_API_KEY=sk-your-key-here
```

## Decision Logic

**Confidence Formula:**
```
Score = ((Evidence_Quality + Data_Completeness) × 50) - (Discrepancy_Penalty + Hype_Penalty)
```

- **Score ≥ 50** → VERIFY (cautious proceed)
- **Score < 50** → REFUSE (too risky)

## Security

- Adversarial defense middleware blocks jailbreak attempts
- All `/api/` POST requests are scanned for manipulation patterns
- Immutable safety rules cannot be overridden by user input
