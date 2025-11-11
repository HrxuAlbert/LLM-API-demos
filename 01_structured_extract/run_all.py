"""
Run all API demos sequentially and compare their outputs.

This script executes structured output extraction using OpenAI, Google Gemini, 
and Anthropic Claude APIs on sample academic paper metadata.
"""
import os
from pathlib import Path
import importlib
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

FILES = ["samples/paper.txt", "samples/paper_noise.txt"]
DRIVERS = [
    ("openai_demo", ["OPENAI_API_KEY"]),
    ("gemini_demo", ["GEMINI_API_KEY", "GOOGLE_API_KEY"]),  # Support both env var names
    ("anthropic_demo", ["ANTHROPIC_API_KEY"]),
]

def main():
    base = Path(__file__).resolve().parent
    ok_any = False
    for mod_name, env_keys in DRIVERS:
        # Check if any of the required environment variables are set
        has_key = any(os.getenv(key) for key in env_keys)
        if not has_key:
            keys_str = " or ".join(env_keys)
            print(f"⚠️  Skip {mod_name}: missing {keys_str}")
            continue
        ok_any = True
        mod = importlib.import_module(mod_name)
        print(f"\n===== {mod_name} =====")
        # Gemini free tier requires rate limiting (5 RPM) - wait before starting
        if mod_name == "gemini_demo":
            print("⏱️  Waiting 15 seconds to avoid Gemini rate limits...")
            time.sleep(15)
        for f in FILES:
            print(f"\n-- File: {f} --")
            try:
                mod.run(f)
                # Add delay between Gemini requests to avoid 503 errors (free tier: 5 RPM)
                if mod_name == "gemini_demo":
                    time.sleep(15)
            except SystemExit as e:
                # Handle SystemExit from validate.py
                msg = str(e) if str(e) else "Validation or parsing error"
                print(f"❌ {msg}")
            except Exception as e:
                # Catch all other exceptions (API errors, network issues, etc.)
                print(f"❌ Error: {type(e).__name__}: {e}")
    if not ok_any:
        print("❌ No API keys configured. Please set environment variables.")

if __name__ == "__main__":
    main()
