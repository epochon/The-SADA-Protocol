# HypeSlayer: A Technical Compendium on AI-Driven Financial Misinformation Detection

## Executive Summary

The digitization of financial markets has democratized access to investment opportunities but simultaneously unleashed a torrent of misinformation. Social media platforms, algorithmically optimized for engagement rather than veracity, have given rise to a new class of market participant: the "finfluencer." While some provide valuable education, a significant cohort leverages emotional manipulation, high-arousal vocal prosody, and deceptive visual aids to promote speculative assets, pump-and-dump schemes, and fraudulent tokens.

HypeSlayer, conceptually designated as "The Skeptic," represents a technological intervention in this epistemic crisis. It is an autonomous, multi-modal artificial intelligence agent designed to audit, quantify, and verify financial content in real-time. Unlike generic summarization tools, HypeSlayer employs a rigorous "Chain of Verification" (CoVe) architecture. It ingests video content, decomposes it into testable claims, and cross-references these claims against immutable market data and on-chain security protocols.

This report provides an exhaustive technical analysis of the HypeSlayer ecosystem. We detail the high-performance backend architecture built on FastAPI and Celery, utilizing the ultra-low latency inference capabilities of Groq and Llama 3.3. We explore the integration of LangChain for orchestrating complex cognitive workflows and the deployment of advanced signal processing via Librosa and OpenSMILE to detect the acoustic signatures of deception. Furthermore, we examine the implementation of computer vision forensics using Llama 3.2 Vision to identify misleading charts and the utilization of GoPlus Security APIs to flag "honeypot" crypto scams. Finally, we outline a novel reputation system anchored in Qdrant vector databases, creating a closed-loop feedback mechanism that holds content creators accountable for their predictions over time.

---

## 1. Introduction: The Epistemic Crisis in Retail Finance

### 1.1 The Architecture of Hype

The modern financial information landscape is characterized by a dangerous decoupling of influence from accuracy. In the pre-digital era, financial advice was largely the purview of regulated entities—broker-dealers, certified financial planners, and institutional analysts—subject to strict compliance frameworks like FINRA Rule 2210. Today, the barrier to entry for disseminating financial advice is a YouTube account and a webcam.

The algorithms powering platforms like TikTok, YouTube, and X (formerly Twitter) prioritize content that elicits strong physiological arousal. In the financial domain, this manifests as "hype": extreme price predictions ("Bitcoin to $1 million by Tuesday"), urgent calls to action ("Buy before it's too late!"), and the demonization of diverse viewpoints. This environment creates a fertile ground for predatory actors to execute pump-and-dump schemes, where the influencer accumulates a micro-cap asset, hypes it to a retail audience to drive up liquidity, and then exits the position into the buying pressure they created.

The challenge for retail investors is epistemic: they lack the tools to rapidly verify claims, analyze the security contracts of new tokens, or assess the historical accuracy of the influencer. Human verification is too slow to match the velocity of social sentiment. By the time a fraudulent claim is debunked by human fact-checkers, the market movement—and the subsequent crash—has often already occurred.

### 1.2 The HypeSlayer Solution: Automated Epistemic Vigilance

HypeSlayer addresses this asymmetry by automating the role of a skeptical financial analyst. It treats every sentence spoken in a financial video not as information to be consumed, but as a hypothesis to be tested. The system is engineered around the principle of **Epistemic Refusal**: the AI is explicitly trained to reject claims that are vague, unfalsifiable, or unsupported by sufficient evidence, rather than hallucinating a probability of truth.

The system operates on three simultaneous planes of analysis:

1. **Semantic Analysis**: What is explicitly stated? (e.g., "Revenue grew 20%").
2. **Acoustic Analysis**: How is it stated? (e.g., High pitch variance indicating stress or artificial excitement).
3. **Visual Analysis**: What is shown? (e.g., A chart with a manipulated Y-axis).

By synthesizing these signals into a composite "Bullshit Score," HypeSlayer provides a quantifiable metric of reliability, effectively acting as a firewall between predatory content and the investor's wallet.

---

## 2. High-Level System Architecture

The architectural requirements for HypeSlayer are dictated by the need for high throughput, low latency, and fault tolerance. Financial data is time-sensitive; a reality check delivered an hour late is useless. Consequently, the system adopts an asynchronous, event-driven microservices architecture.

### 2.1 The Modular Monolith Approach

While microservices offer scalability, they introduce complexity in deployment and inter-service communication. For the current iteration of HypeSlayer, we utilize a **Modular Monolith** pattern. This structure allows distinct domains (Ingestion, Analysis, Verification, Reporting) to coexist within a single deployable unit while maintaining strict boundary separation, facilitating an easy migration to distributed microservices as scaling demands increase.

### 2.2 Core Architectural Components

The system is composed of five primary layers, each responsible for a distinct stage of the data lifecycle:

1. **Ingestion Layer**: This layer handles the asynchronous retrieval of multi-modal data. It interfaces with external content platforms (YouTube) to fetch metadata, video streams, and transcripts. It must handle API rate limits, transient network failures, and diverse media formats.

2. **Orchestration Layer (The "Cortex")**: Built on LangChain, this layer serves as the central nervous system. It routes tasks to specialized sub-agents, manages the state of the analysis, and ensures that dependencies (e.g., waiting for entity extraction before triggering market data lookups) are respected.

3. **Analysis Layer (The Signal Processors)**:
   - **Text Agent**: Utilizes Large Language Models (LLMs) to parse natural language into structured claims.
   - **Audio Agent**: Employs digital signal processing (DSP) to quantify vocal stress and emotional arousal.
   - **Vision Agent**: Uses Vision-Language Models (VLMs) to perform optical character recognition (OCR) and semantic interpretation of financial charts.

4. **Verification Layer (The "Judge")**: This layer connects to the external world of hard data. It queries financial APIs (yfinance, Alpha Vantage) and blockchain security scanners (GoPlus, Honeypot.is) to validate the claims extracted by the analysis layer.

5. **Persistence & Memory Layer**: Utilizing Qdrant for vector storage and PostgreSQL for relational data, this layer maintains the long-term history of influencers, enabling the calculation of longitudinal reputation scores.

### 2.3 Data Flow Pipeline

The data flow through HypeSlayer is linear but highly parallelized. When a user submits a URL, the system initiates a cascade of operations designed to minimize total processing time.

The request enters via a FastAPI endpoint, which immediately offloads the heavy processing to a Celery task queue backed by Redis. This separation is critical; identifying financial entities and fetching their real-time market data can take several seconds, while full audio/video analysis can take minutes. The user receives a job ID immediately, allowing the frontend to poll for updates or establish a WebSocket connection for real-time progress reporting.

Inside the worker process, the pipeline forks. One branch processes the transcript for semantic claims. Another processes the audio track for prosodic features. A third samples video frames for visual analysis. These parallel streams converge at the Decision Gate, where the scoring algorithm synthesizes the multi-modal evidence into a final verdict.

---

## 3. The Backend Core: High-Performance Python

The backbone of HypeSlayer is built on Python, the lingua franca of both AI and quantitative finance. However, standard Python web frameworks like Flask are synchronous (blocking), making them unsuitable for I/O-heavy applications that rely on multiple external APIs.

### 3.1 Framework Selection: FastAPI

FastAPI was selected as the primary web framework due to its native support for Python's `asyncio` event loop. In a financial context, milliseconds matter. FastAPI allows the server to handle thousands of concurrent analysis requests by suspending execution while waiting for external responses (e.g., from Groq or yfinance) rather than blocking the entire thread.

**Key technical advantages utilized in HypeSlayer include:**

- **Pydantic Integration**: Financial data requires strict schema validation. FastAPI's deep integration with Pydantic ensures that all incoming requests and outgoing JSON responses adhere to rigorous type definitions. If the LLM generates a malformed JSON object, Pydantic validation catches it before it reaches the frontend.

- **Dependency Injection**: FastAPI's dependency injection system simplifies the management of database sessions and API clients, allowing for easy mocking during unit testing—a critical requirement for financial software where reliability is paramount.

### 3.2 Asynchronous Task Management with Celery

While `asyncio` handles I/O-bound concurrency, CPU-bound tasks—such as computing the Short-Time Fourier Transform (STFT) of an audio signal or running OCR on video frames—must be offloaded to prevent blocking the event loop.

HypeSlayer employs **Celery**, a distributed task queue, paired with **Redis** as the message broker.

- **Task Routing**: Short, interactive tasks (e.g., "Check current price of $TSLA") are routed to a high-priority queue. Long-running analysis tasks (e.g., "Analyze this 1-hour podcast") are routed to a background queue.

- **Reliability**: Celery provides "at-least-once" delivery semantics. If a worker crashes mid-analysis, the task is re-queued, ensuring that no user request is lost in the ether. This is essential for building a robust, production-grade system.

---

## 4. The Cognitive Engine: LLM & LangChain Integration

The "brain" of HypeSlayer is a Large Language Model (LLM) orchestrated by LangChain. The system moves beyond simple prompt-response interactions, utilizing an agentic workflow where the LLM can use tools, make decisions, and reflect on its own outputs.

### 4.1 Inference Engine: Groq + Llama 3.3

The efficacy of an interactive agent is directly correlated with its latency. Traditional LLM providers can have token generation speeds that make real-time analysis feel sluggish. HypeSlayer leverages **Groq**, a specialized LPU (Language Processing Unit) provider, which delivers inference speeds exceeding **500 tokens per second** for Llama 3 models.

- **Model Selection**: Llama 3.3 70B is the primary driver for complex reasoning tasks. Its massive parameter count allows it to understand nuance, sarcasm, and complex financial jargon that smaller models might miss.

- **Speed as a Feature**: The high speed of Groq allows HypeSlayer to employ "Chain of Thought" (CoT) prompting without imposing unacceptable wait times on the user. The model can generate hundreds of words of internal reasoning—weighing evidence, considering counter-arguments—in a fraction of a second before producing its final output.

### 4.2 Orchestration: LangGraph & Plan-and-Execute

Early versions of AI agents relied on the **ReAct** (Reason + Act) pattern, where the model decides on one action, executes it, observes the result, and then decides the next action. While flexible, this can be slow and prone to getting stuck in loops.

HypeSlayer utilizes the **Plan-and-Execute** pattern implemented via LangGraph.

- **Planner**: The agent first generates a comprehensive plan. For a video about "Top 5 Crypto Picks," the plan might be: "1. Extract tickers. 2. For each ticker, fetch price. 3. Check for honeypot status. 4. Compare prediction to consensus."

- **Executor**: A separate, lighter-weight agent (or a parallelized set of workers) executes these steps. This allows for massive parallelism—all 5 crypto tickers can be checked simultaneously rather than sequentially.

- **Replanner**: If a step fails (e.g., "Ticker $SCAM not found on yfinance"), the replanner assesses whether to try a different data source (e.g., DEX Screener) or mark the claim as unverifiable.

### 4.3 Prompt Engineering: The "Skeptic" Persona

The prompt engineering strategy focuses on **Epistemic Rigor**. The system instructions explicitly forbid the model from "filling in the blanks."

**Input**: "This coin is going to the moon!"

**Bad Output**: "Prediction: Price will rise significantly." (Too vague).

**HypeSlayer Output**: "Claim: 'Going to the moon'. Metric: Unspecified. Target: None. Timeframe: None. Verdict: UNVERIFIABLE HYPE."

This distinct "Skeptic" persona ensures that the user understands the difference between a verifiable financial forecast and empty rhetoric.

---

## 5. Multimodal Hype Detection: Signal Processing

Financial hype is rarely conveyed through text alone. It is a multimodal phenomenon involving vocal modulation (shouting, rapid speech) and visual manipulation (flashy graphics, misleading charts). HypeSlayer integrates distinct processing pipelines to analyze these signals.

### 5.1 Acoustic Analysis: The Sound of Hype

High-pressure sales tactics, common in pump-and-dump schemes, often manifest in specific prosodic features. Research in psychoacoustics suggests that increased pitch variance and articulation rate are correlated with high emotional arousal, which can inhibit critical thinking in listeners.

**Technology Stack:**
- **Librosa**: A Python library for music and audio analysis.
- **OpenSMILE**: A feature extraction toolkit specifically designed for emotion recognition in speech.

**Key Acoustic Metrics:**

1. **Fundamental Frequency (F0) Variance**: Using Librosa's `piptrack` or `pyin` algorithms, we extract the pitch contour of the speaker. High standard deviation in F0 often indicates exaggerated emotionality, distinct from the natural intonation of conversational speech.

2. **Articulation Rate**: HypeSlayer calculates the number of syllables spoken per second during claim-heavy segments. Rapid speech ("firehosing") is a known persuasion tactic. We utilize algorithms that detect syllable nuclei (peaks in intensity preceded/followed by dips) to quantify this rate.

3. **Jitter and Shimmer**: These measure micro-fluctuations in pitch and loudness, respectively. High levels of jitter and shimmer are often biomarkers of physiological stress or cognitive load.

**Processing Pipeline:**

The audio is extracted via `ffmpeg`, downsampled to 16kHz mono to reduce bandwidth, and segmented based on the timestamps of financial claims. If the segment containing "This is a guaranteed 100x!" exhibits F0 variance > 2 standard deviations above the speaker's baseline, the Hype Penalty is increased.

### 5.2 Visual Forensics: Chart Analysis

A common technique in misleading financial content is the manipulation of visual data—truncating the Y-axis to make small gains look massive, or comparing assets with different scales without normalization.

**Technology Stack:**
- **Llama 3.2 Vision (11B/90B)**: As a Vision-Language Model (VLM), Llama 3.2 can ingest images and answer questions about them.

**Workflow:**

1. **Keyframe Extraction**: The system scans the video for frames containing keywords like "Chart," "Price," or "Analysis."

2. **Structured Extraction**: The VLM is prompted to extract the Axis Labels, Time Range, and Trend Direction into a JSON format.
   - **Prompt**: "Analyze this stock chart. Identify the X-axis time range, the Y-axis price range, and the asset name. Does the chart start at zero? Is the scale linear or logarithmic?".

3. **Cross-Verification**: The system compares the visual data against yfinance.
   - **Scenario**: Video shows a chart where the price line goes up 45 degrees.
   - **Reality**: yfinance data for that period shows a flat trend.
   - **Verdict**: Visual Hallucination Detected.

---

## 6. The Verification Engine: Data Sources & Forensics

The core value proposition of HypeSlayer is its ability to check claims against ground truth. This requires a robust integration of external data APIs covering both traditional finance (TradFi) and decentralized finance (DeFi).

### 6.1 Traditional Markets: yfinance & Alpha Vantage

For equities (stocks) and major cryptocurrencies (Bitcoin, Ethereum), **yfinance** serves as the primary data source due to its comprehensive coverage and zero cost.

**Implementation Strategy:**

The `MarketDataService` abstracts the complexity of data fetching. When the LLM extracts a ticker like "$GME," the service:

1. **Resolves the Ticker**: Ensures "GME" refers to GameStop on NYSE.

2. **Fetches History**: `yf.Ticker("GME").history(period="1mo")` retrieves the Open, High, Low, Close (OHLC) data.

3. **Calculates Derived Metrics**:
   - **Volatility**: Calculating the beta or standard deviation of returns to assess risk.
   - **Trend**: Comparing the Short-Term Moving Average (SMA-50) vs. Long-Term (SMA-200) to verify "bull market" claims.

**Fallback Redundancy**: If yfinance fails or rate-limits the request, the system fails over to **Alpha Vantage**, which provides a stable, key-based API for core market data.

### 6.2 On-Chain Forensics: The Anti-Rug Pull System

For "memecoins" and low-cap crypto assets, price data is insufficient. A token price might be rising simply because investors are unable to sell (a "honeypot"). HypeSlayer integrates specific DeFi security APIs to detect these malicious contract mechanics.

**Technology Stack:**
- **GoPlus Security API**: Provides real-time risk assessment for token contracts.
- **Honeypot.is API**: Simulates transactions to verify sellability.

**Scam Detection Workflow:**

1. **Contract Extraction**: The LLM scans the video description and pinned comments for hexadecimal strings (`0x...`) which typically denote contract addresses.

2. **Security Audit**: The extracted address is sent to the GoPlus `token_security` endpoint. The system checks specific flags:
   - `is_honeypot`: If "1", the token cannot be sold. **Critical Flag**.
   - `buy_tax` / `sell_tax`: Taxes above 10% are flagged as predatory.
   - `owner_change_balance`: If "1", the contract owner can arbitrarily modify user balances.

3. **Liquidity Analysis**: Using DEX Screener, the system checks the liquidity depth. A token with $1M market cap but only $500 in liquidity is flagged as a high slippage/rug pull risk.

Any critical flag triggers an immediate "Scam Alert" on the frontend, overriding all other analysis.

---

## 7. The Scoring Algorithm: Quantifying "Bullshit"

To provide a quick, actionable insight for the user, HypeSlayer condenses its multi-modal analysis into a single metric: the **Bullshit Score**. This is not a random number but the result of a deterministic algorithm.

### 7.1 The Composite Formula

The Bullshit Score ($B$) is calculated as a weighted average of three sub-components, adjusted by a credibility modifier:

$$B = \text{clamp}\left( \frac{w_H \cdot H + w_D \cdot D + w_F \cdot F}{w_H + w_D + w_F} \times (1 + P_{rep}), 0, 100 \right)$$

**Where:**

- $H$ (**Hype Intensity**): A normalized score (0-100) derived from:
  - **Sentiment**: VADER compound score (0.0 to 1.0) scaled to 0-50.
  - **Vocal Stress**: Librosa F0 variance > 2σ adds 25 points.
  - **Keywords**: "Guaranteed," "1000x," "Mortgage" adds 5 points each.

- $D$ (**Data Divergence**): The discrepancy between the claim and reality.
  - If Claim = "Bullish" and Market Data = "Bearish", $D = 100$.
  - If Claim matches Data, $D = 0$.

- $F$ (**Forensic Risk**): Binary flags from GoPlus/Honeypot.is.
  - If `is_honeypot == 1`, $F = 100$ and $w_F$ becomes infinite (overriding score to 100).

- $P_{rep}$ (**Reputation Penalty**): A modifier based on the influencer's history (see Section 8). If they have a history of failed predictions, this penalty increases the base score.

### 7.2 Semantic Sentiment with VADER

We utilize **VADER** (Valence Aware Dictionary and sEntiment Reasoner) for text sentiment. Unlike general NLP models, VADER is attuned to social media contexts. It correctly interprets:

- **Capitalization**: "BUY NOW" scores higher intensity than "buy now."
- **Punctuation**: "Moon!!!" scores higher than "Moon."
- **Emoticons**: "🚀" and "💎🙌" are mapped to high positive intensity.

HypeSlayer extends the default VADER lexicon with a **custom financial dictionary**, ensuring terms like "rug pull" (negative) and "ATH" (All Time High - positive) are correctly scored.

---

## 8. Reputation & Memory: The "Architect-in-the-Loop"

Most analysis tools are stateless; they judge a video in isolation. HypeSlayer implements **Long-Term Memory** to track influencer credibility over time, creating a reputation system that rewards accuracy and penalizes hyperbole.

### 8.1 Vector Database Integration (Qdrant)

We employ **Qdrant**, a high-performance open-source vector database, to store the "DNA" of every analyzed claim.

**Storage Schema:**

Every extracted claim is vectorized (using `all-MiniLM-L6-v2`) and stored with a metadata payload:

```json
{
  "vector": [0.12, -0.05, ...],
  "payload": {
    "influencer_id": "UC_xyz123",
    "claim_text": "Bitcoin will hit $100k by Dec 2025",
    "asset": "BTC",
    "target_price": 100000,
    "prediction_date": "2024-01-01",
    "status": "PENDING"
  }
}
```

This allows for **semantic search**. A user can ask, "Has this guy ever been wrong about Bitcoin?" and the system can retrieve semantically similar past claims and their outcomes.

### 8.2 The Closed-Loop Feedback System

To verify predictions that have a future time horizon, HypeSlayer uses **APScheduler**.

1. **Scheduling**: When a claim with a date ("by next month") is detected, the system schedules a background job.

2. **Verification**: On the target date, the job triggers. It fetches the historical price for that asset on that specific day using yfinance.

3. **Scoring**:
   - If the prediction was correct (within a margin of error), the influencer's **Credibility Score** ($C_{cred}$) increases.
   - If incorrect, $C_{cred}$ decreases.

4. **Feedback**: This updated credibility score is fed back into the Bullshit Score algorithm ($P_{rep}$) for future videos. An influencer with a 10% accuracy rate will start every new analysis with a "high bullshit" handicap.

---

## 9. Frontend Visualization & User Experience

The frontend, built with **Next.js** and **Tailwind CSS**, focuses on "Explainable AI." It is not enough to give a score; the user must understand why the score was given.

### 9.1 Interactive "Reality Ribbons"

Using **Plotly.js**, we create a custom "Reality Ribbon" chart.

- **The Concept**: A timeline under the video player that visualizes the density of hype vs. fact.

- **Implementation**: The X-axis represents the video duration. The ribbon color gradients from Green (Verifiable Fact) to Red (Unverified Hype).

- **Interaction**: Users can click on a "Red" section of the ribbon. The video player jumps to that timestamp, and a sidebar displays the specific contradiction (e.g., "Influencer claims 'Massive Profit', but Q3 Earnings Report shows Net Loss").

### 9.2 Sentiment Heatmaps

For channel-level analysis, we use Plotly heatmaps to visualize an influencer's sentiment over time.

- **Y-Axis**: Asset Classes (Crypto, Tech Stocks, ETFs).
- **X-Axis**: Time (Months).
- **Cell Color**: Accuracy of prediction.

This visualization instantly reveals bias. A user might see that an influencer is highly accurate on Tech Stocks (Green cells) but consistently wrong on Crypto (Red cells).

---

## 10. Regulatory Compliance & Ethical Design

In the financial domain, AI hallucinations can lead to real monetary loss. HypeSlayer is designed with strict adherence to emerging regulatory frameworks regarding AI financial advice.

### 10.1 Anti-AI Washing & SEC Compliance

The SEC has warned against "AI Washing"—making exaggerated claims about AI capabilities. HypeSlayer addresses this through:

- **Traceability**: Every output is linked to a specific data source (e.g., "Source: Yahoo Finance API, retrieved 2025-10-12").

- **No "Black Box" Advice**: The system never advises "Buy" or "Sell." It only outputs "Verified" or "Unverified."

- **Disclaimers**: Prominent disclosures stating the tool is an informational filter, not a financial advisor.

### 10.2 Epistemic Refusal as a Safety Feature

The most dangerous failure mode for an AI is confidence in ignorance. HypeSlayer's prompt engineering enforces **Epistemic Refusal**. If the audio quality prevents accurate transcription, or if the ticker symbol is ambiguous (e.g., "ETH" could be Ethereum or a furniture retailer), the system outputs a specific "Refusal Code" rather than guessing. This conservative approach builds user trust; when the system does speak, it speaks with data-backed authority.

---

## 11. Deployment & DevOps Strategy

To transition from a hackathon prototype to a production-grade service, HypeSlayer employs a containerized DevOps strategy.

### 11.1 Docker Containerization

The backend is packaged as a Docker container based on `python:3.11-slim`. Multi-stage builds are used to minimize image size:

- **Builder Stage**: Compiles dependencies and wheels.
- **Runtime Stage**: Copies only necessary artifacts, keeping the final image lightweight for fast deployment.

### 11.2 CI/CD & Environment Management

- **GitHub Actions**: Pipelines run automated tests (Pytest) and linting (Ruff) on every commit.

- **Secret Management**: Sensitive API keys (Groq, GoPlus, Alpha Vantage) are never hardcoded. They are injected at runtime via `.env` files managed by the hosting platform (e.g., Railway or Vercel), utilizing `python-dotenv` for local development security.

---

## 12. Future Directions

The modular architecture of HypeSlayer allows for significant future expansion:

1. **Browser Extension**: Injecting the "Bullshit Score" directly onto the YouTube interface, functioning like an ad-blocker for financial misinformation.

2. **Live Stream Analysis**: Implementing WebSocket support to process live audio streams from earnings calls or Fed announcements in real-time.

3. **Federated Learning**: Allowing users to "vote" on the accuracy of the AI's verdict, creating a labeled dataset to fine-tune a smaller, open-source LoRA adapter for specialized financial scam detection.

---

## 13. Conclusion

HypeSlayer is more than a technical demonstration; it is a proof-of-concept for a new layer of the financial internet. By combining the semantic understanding of Large Language Models with the objective rigidity of market data APIs and the forensic capabilities of signal processing, it offers a scalable solution to the problem of financial misinformation.

The system demonstrates that AI need not be a generator of noise; properly architected, it can be the ultimate filter. Through its rigorous "Verify, Don't Trust" architecture, HypeSlayer restores a measure of epistemic sanity to the chaotic world of retail investing.

**HypeSlayer: Protecting investors, one video at a time.**

---

## Technical Stack Summary

| Component | Technology | Function |
|-----------|-----------|----------|
| **Framework** | FastAPI (Python) | High-performance asynchronous API handling |
| **Inference** | Groq (Llama 3.3) | Ultra-low latency semantic reasoning |
| **Orchestrator** | LangChain / LangGraph | Complex agentic workflows and planning |
| **Market Data** | yfinance / Alpha Vantage | Real-time equity and crypto price verification |
| **Security** | GoPlus / Honeypot.is | On-chain forensic analysis for scam tokens |
| **Audio DSP** | Librosa / OpenSMILE | Vocal stress and hype detection |
| **Vision** | Llama 3.2 Vision | Chart OCR and visual manipulation detection |
| **Memory** | Qdrant (Vector DB) | Long-term influencer reputation tracking |
| **Frontend** | Next.js + Plotly | Interactive dashboards and data visualization |
| **Tasks** | Celery + Redis | Distributed background task processing |
