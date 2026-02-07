"""
Quick test script to verify Groq integration
"""
from dotenv import load_dotenv
import os

load_dotenv()

key = os.getenv("GROQ_API_KEY")
print(f"🔑 Groq Key Found: {'Yes ✅' if key else 'No ❌'}")

if key:
    try:
        from app.agent.hypeslayer_llm import hypeslayer_llm
        
        # Test entity extraction
        test_transcript = "I think GameStop stock (GME) will hit $500 by next month! This is going to the moon!"
        
        print("\n🧪 Testing Entity Extraction...")
        print(f"Input: {test_transcript}\n")
        
        result = hypeslayer_llm.extract_entities(test_transcript)
        
        print("✅ Extraction Result:")
        print(f"  Ticker: {result.ticker}")
        print(f"  Asset Type: {result.asset_type}")
        print(f"  Claim: {result.claim}")
        print(f"  Timeline: {result.timeline}")
        print(f"  Confidence: {result.confidence}")
        
        if result.refusal_reason:
            print(f"  ⚠️ Refusal: {result.refusal_reason}")
        
        print("\n🎉 Groq integration working perfectly!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Make sure you've added GROQ_API_KEY to backend/.env")
else:
    print("\n❌ Please add GROQ_API_KEY to backend/.env")
    print("Get free key from: https://console.groq.com/keys")
