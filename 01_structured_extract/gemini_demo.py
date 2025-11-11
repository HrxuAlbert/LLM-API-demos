import os, argparse, json, sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

sys.path.append(str(Path(__file__).resolve().parent))

from google import genai
from common.validate import load_text, parse_json, validate_and_print, save_json
from common.schema import PAPER_SCHEMA, SYSTEM_INSTRUCTION

DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

def _extract_json_from_response(resp) -> str:
    """Extract JSON string from Gemini response.
    
    The newer SDK version supports resp.text directly. 
    If not available, fallback to concatenating parts from candidates.
    """
    if getattr(resp, "text", None):
        return resp.text
    # Fallback: concatenate text from all candidate parts
    parts = []
    for cand in getattr(resp, "candidates", []):
        for p in getattr(cand, "content", {}).get("parts", []):
            if "text" in p:
                parts.append(p["text"])
    return "\n".join(parts).strip()

def run(file_path: str) -> dict:
    # Prefer GEMINI_API_KEY (official), fallback to GOOGLE_API_KEY (backward compatibility)
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    client = genai.Client(api_key=api_key)
    text = load_text(file_path)
    prompt = f"{SYSTEM_INSTRUCTION}\nText:\n{text}"

    resp = client.models.generate_content(
        model=DEFAULT_MODEL,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_json_schema": PAPER_SCHEMA
        }
    )

    raw = _extract_json_from_response(resp)
    data = parse_json(raw)

    # Print token usage if available
    um = getattr(resp, "usage_metadata", None)
    if um:
        print(f"[Gemini usage] input={getattr(um,'prompt_token_count',None)} "
              f"output={getattr(um,'candidates_token_count',None)} total={getattr(um,'total_token_count',None)}")

    validate_and_print(data, PAPER_SCHEMA)
    stem = Path(file_path).stem
    save_json(data, f"outputs/gemini_{stem}.json")
    return data

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", default="samples/paper.txt", help="Path to input file (e.g., samples/paper.txt or samples/paper_noise.txt)")
    args = parser.parse_args()
    run(args.file)
