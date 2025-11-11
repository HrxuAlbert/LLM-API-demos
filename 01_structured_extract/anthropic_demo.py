import os, argparse, sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

sys.path.append(str(Path(__file__).resolve().parent))

import anthropic
from common.validate import load_text, validate_and_print, save_json
from common.schema import PAPER_SCHEMA, SYSTEM_INSTRUCTION

DEFAULT_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5")

def _find_tool_args(msg) -> dict | None:
    """Extract tool call arguments from Claude's response message.
    
    Claude returns content as a list of blocks (TextBlock or ToolUseBlock).
    This function searches for the 'submit_extraction' tool call and returns its input.
    """
    for block in msg.content:
        # Support both object attribute access and dict-style access
        btype = getattr(block, "type", None) or (isinstance(block, dict) and block.get("type"))
        if btype == "tool_use":
            name = getattr(block, "name", None) or block.get("name")
            if name == "submit_extraction":
                return getattr(block, "input", None) or block.get("input")
    return None

def run(file_path: str) -> dict:
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    text = load_text(file_path)

    tools = [{
        "name": "submit_extraction",
        "description": "Return the extracted metadata strictly following the input schema.",
        "input_schema": PAPER_SCHEMA
    }]

    msg = client.messages.create(
        model=DEFAULT_MODEL,
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": f"{SYSTEM_INSTRUCTION}\nText:\n{text}\nReturn via tool only."
        }],
        tools=tools,
        tool_choice={"type": "tool", "name": "submit_extraction"},
        temperature=0
    )

    args = _find_tool_args(msg)
    if args is None:
        raise SystemExit("Claude did not call submit_extraction — check prompt/model.")

    # Print token usage if available
    u = getattr(msg, "usage", None)
    if u:
        print(f"[Anthropic usage] input={getattr(u,'input_tokens',None)} output={getattr(u,'output_tokens',None)}")

    validate_and_print(args, PAPER_SCHEMA)
    stem = Path(file_path).stem
    save_json(args, f"outputs/anthropic_{stem}.json")
    return args

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", default="samples/paper.txt", help="Path to input file (e.g., samples/paper.txt or samples/paper_noise.txt)")
    args = parser.parse_args()
    run(args.file)
