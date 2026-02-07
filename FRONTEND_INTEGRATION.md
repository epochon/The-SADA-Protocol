# 🎨 Frontend Integration Guide

**How to integrate HypeSlayer backend with your UI**

---

## 🚀 Quick Start

1. **Backend is running at:** `http://localhost:8000`
2. **API Docs:** `http://localhost:8000/docs`
3. **CORS enabled for:** `http://localhost:3000`

---

## 📦 Recommended Frontend Flow

### Step 1: User Inputs YouTube URL

```jsx
const [videoUrl, setVideoUrl] = useState('');
const [analysis, setAnalysis] = useState(null);
const [loading, setLoading] = useState(false);

const analyzeVideo = async () => {
  setLoading(true);
  
  try {
    // 1. Fetch transcript
    const transcriptRes = await fetch('http://localhost:8000/hypeslayer/ingest-video', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ video_url: videoUrl })
    });
    const { transcript } = await transcriptRes.json();
    
    // 2. Extract entities
    const entitiesRes = await fetch('http://localhost:8000/hypeslayer/parse-entities', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ transcript })
    });
    const entities = await entitiesRes.json();
    
    // 3. Analyze sentiment
    const sentimentRes = await fetch('http://localhost:8000/hypeslayer/analyze-sentiment', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: transcript })
    });
    const sentiment = await sentimentRes.json();
    
    // 4. Calculate bullshit score
    const bsRes = await fetch('http://localhost:8000/hypeslayer/bullshit-score', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        ticker: entities.ticker || 'UNKNOWN',
        data_availability: !!entities.ticker 
      })
    });
    const bullshitScore = await bsRes.json();
    
    // 5. Make final decision
    const decisionRes = await fetch('http://localhost:8000/hypeslayer/calculate-confidence', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        evidence_quality: entities.confidence,
        data_completeness: 0.8,
        risk_penalty: bullshitScore.bullshit_score > 50 ? 40 : 10,
        hype_penalty: sentiment.hype_penalty
      })
    });
    const decision = await decisionRes.json();
    
    // Update UI with results
    setAnalysis({
      entities,
      sentiment,
      bullshitScore,
      decision
    });
    
  } catch (error) {
    console.error('Analysis failed:', error);
  } finally {
    setLoading(false);
  }
};
```

---

## 🎨 UI Components to Build

### 1. Video Input Component
```jsx
<div className="video-input">
  <input 
    type="text" 
    placeholder="Paste YouTube URL..." 
    value={videoUrl}
    onChange={(e) => setVideoUrl(e.target.value)}
  />
  <button onClick={analyzeVideo} disabled={loading}>
    {loading ? 'Analyzing...' : 'Analyze Video'}
  </button>
</div>
```

### 2. Hype Meter Visualization
```jsx
{analysis && (
  <div className="hype-meter">
    <h3>Hype Level: {analysis.sentiment.hype_level}</h3>
    <div className="meter-bar">
      <div 
        className="meter-fill"
        style={{ 
          width: `${analysis.sentiment.sentiment_score * 100}%`,
          backgroundColor: analysis.sentiment.hype_level === 'EXTREME' ? 'red' : 'orange'
        }}
      />
    </div>
    <p>Penalty: {analysis.sentiment.hype_penalty} points</p>
  </div>
)}
```

### 3. Bullshit Score Display
```jsx
{analysis && (
  <div className="bullshit-score">
    <h2>💩 Bullshit Score: {analysis.bullshitScore.bullshit_score}/100</h2>
    <p>{analysis.bullshitScore.reason}</p>
    {analysis.bullshitScore.auto_refuse && (
      <div className="alert-danger">
        ⚠️ AUTO-REFUSED: This ticker is highly suspicious!
      </div>
    )}
  </div>
)}
```

### 4. Final Decision Card
```jsx
{analysis && (
  <div className={`decision-card ${analysis.decision.decision.toLowerCase()}`}>
    <h1>{analysis.decision.decision}</h1>
    <p>Confidence: {analysis.decision.confidence_score.toFixed(1)}/100</p>
    <ul>
      {analysis.decision.reasoning.map((reason, i) => (
        <li key={i}>{reason}</li>
      ))}
    </ul>
  </div>
)}
```

### 5. Entity Display
```jsx
{analysis && analysis.entities.ticker && (
  <div className="entity-card">
    <h3>Detected: {analysis.entities.ticker}</h3>
    <p>Type: {analysis.entities.asset_type}</p>
    <p>Claim: {analysis.entities.claim}</p>
    <p>Timeline: {analysis.entities.timeline}</p>
  </div>
)}
```

---

## 🎭 Suggested UI States

### Loading State
```jsx
{loading && (
  <div className="loading-spinner">
    <div className="spinner" />
    <p>Scanning video for financial claims...</p>
  </div>
)}
```

### Error State
```jsx
{error && (
  <div className="error-message">
    <h3>❌ Analysis Failed</h3>
    <p>{error}</p>
  </div>
)}
```

### Empty State
```jsx
{!analysis && !loading && (
  <div className="empty-state">
    <h2>🛡️ HypeSlayer</h2>
    <p>Paste a YouTube video URL to detect financial BS</p>
  </div>
)}
```

---

## 🎨 Design Recommendations

### Color Scheme
- **REFUSE (Red)**: `#ef4444` - Danger, high risk
- **VERIFY (Green)**: `#10b981` - Safe, verified
- **EXTREME Hype (Red)**: `#dc2626`
- **HIGH Hype (Orange)**: `#f97316`
- **MODERATE Hype (Yellow)**: `#fbbf24`
- **LOW Hype (Green)**: `#22c55e`

### Animations
- **Hype Meter**: Animated fill from 0 to score
- **Decision Reveal**: Fade in with scale effect
- **Loading**: Pulsing spinner

---

## 📊 Data Structure Reference

```typescript
interface AnalysisResult {
  entities: {
    asset_type: 'stock' | 'crypto' | 'commodity' | 'unknown';
    ticker: string | null;
    claim: string | null;
    timeline: string | null;
    confidence: number;
    refusal_reason: string | null;
  };
  sentiment: {
    sentiment_score: number;
    hype_level: 'EXTREME' | 'HIGH' | 'MODERATE' | 'LOW';
    hype_penalty: number;
    emotional_intensity: 'high' | 'moderate' | 'low';
  };
  bullshitScore: {
    bullshit_score: number;
    reason: string;
    auto_refuse: boolean;
  };
  decision: {
    confidence_score: number;
    decision: 'REFUSE' | 'VERIFY';
    threshold: number;
    reasoning: string[];
  };
}
```

---

## 🧪 Test URLs for Demo

### Scam Video (Should REFUSE)
```
https://www.youtube.com/watch?v=... (find a pump-and-dump video)
```

### Legitimate News (Should VERIFY)
```
https://www.youtube.com/watch?v=... (find a CNBC earnings report)
```

---

## 🐛 Debugging Tips

1. **Check CORS**: Make sure frontend runs on `http://localhost:3000`
2. **Check Backend**: Visit `http://localhost:8000/hypeslayer/health`
3. **Check Logs**: Backend logs show in terminal
4. **Test Individual Endpoints**: Use Swagger UI at `/docs`

---

## 📞 Need Help?

- **API Docs**: `backend/HYPESLAYER_API.md`
- **Backend Team**: Check main README
- **Swagger UI**: `http://localhost:8000/docs`

---

## 🚀 Ready to Build!

Your backend is fully functional. Focus on making the UI **stunning** and **intuitive**!

**Remember**: The goal is to make users feel like they have a skeptical financial advisor protecting them from scams. 🛡️
