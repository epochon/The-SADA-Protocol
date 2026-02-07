# 🦅 Setting up Alpha Vantage for Real-Time Data

Alpha Vantage provides a free API for real-time stock data.

## Step 1: Get Free Key
1.  Go to [Alpha Vantage Claim Key](https://www.alphavantage.co/support/#api-key).
2.  Fill in the form (Organization can be "SADA Protocol").
3.  Click **Get Free API Key**.
4.  Copy your key.

## Step 2: Configure Environment
1.  Open your `.env` file in the `backend/` folder.
2.  Add your key:

```env
ALPHAVANTAGE_API_KEY="your_api_key_here"
```

## Step 3: Verify
Restart your backend (`uvicorn`) and check the console. You should see:
`✅ Alpha Vantage Initialized`

If the key is invalid or rate limited (5 calls/min), the system will automatically fall back to Yahoo Finance so nothing breaks.
