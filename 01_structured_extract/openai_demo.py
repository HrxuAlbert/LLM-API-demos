import os, argparse
from pathlib import Path
import sys, json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add parent directory to path for relative imports
sys.path.append(str(Path(__file__).resolve().parent))

from openai import OpenAI
from common.validate import load_text, parse_json, validate_and_print, save_json
from common.schema import PAPER_SCHEMA, SYSTEM_INSTRUCTION

DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-2024-08-06")

def run(file_path: str) -> dict:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    text = load_text(file_path)

    resp = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_INSTRUCTION},
            {"role": "user", "content": f"Text:\n{text}\nReturn JSON only."}
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "PaperMeta",
                "schema": PAPER_SCHEMA,
                "strict": True
            }
        },
        temperature=0,
    )

    content = resp.choices[0].message.content
    data = parse_json(content)

    # Print token usage if available
    u = getattr(resp, "usage", None)
    if u:
        print(f"[OpenAI usage] prompt={u.prompt_tokens} completion={u.completion_tokens} total={u.total_tokens}")

    # Validate and save results
    validate_and_print(data, PAPER_SCHEMA)
    stem = Path(file_path).stem
    save_json(data, f"outputs/openai_{stem}.json")
    return data

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", default="samples/paper.txt", help="Path to input file (e.g., samples/paper.txt or samples/paper_noise.txt)")
    args = parser.parse_args()
    run(args.file)
