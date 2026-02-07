from dotenv import load_dotenv
import os
from alpha_vantage.timeseries import TimeSeries
import json

load_dotenv()

key = os.getenv("ALPHAVANTAGE_API_KEY")
print(f"🔑 Key Found: {'Yes' if key else 'No'}")

if key:
    try:
        ts = TimeSeries(key=key, output_format='json')
        # Test fetching RELIANCE.BSE
        print("🦅 Fetching RELIANCE.BSE from Alpha Vantage...")
        data, meta_data = ts.get_quote_endpoint(symbol='RELIANCE.BSE')
        print("\n✅ SUCCESS! Current Data:")
        print(json.dumps(data, indent=2))
    except Exception as e:
        print(f"\n❌ FAILED: {e}")
        print("Note: If error is '5 calls per minute', wait and try again.")
else:
    print("❌ Please add ALPHAVANTAGE_API_KEY to backend/.env")
