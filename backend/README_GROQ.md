# 🦙 Getting Your FREE Groq API Key

Groq provides ultra-fast LLM inference (500+ tokens/sec) with a generous free tier.

## Step 1: Sign Up
1. Go to [console.groq.com](https://console.groq.com)
2. Click "Sign Up" (use Google/GitHub for fastest signup)
3. Verify your email

## Step 2: Create API Key
1. Once logged in, go to [API Keys](https://console.groq.com/keys)
2. Click "Create API Key"
3. Give it a name (e.g., "HypeSlayer")
4. Copy the key (starts with `gsk_...`)

## Step 3: Add to .env
Open `backend/.env` and add:
```
GROQ_API_KEY=gsk_your_key_here
```

## ✅ That's it!
Your HypeSlayer agent will now use Groq's Llama 3.3 70B model - **FREE and 10x faster than GPT-4**!

## Free Tier Limits
- **Requests**: 30 requests/minute
- **Tokens**: 6,000 tokens/minute
- **Perfect for**: Hackathons, demos, prototypes

More than enough for your 10-hour hackathon! 🚀
