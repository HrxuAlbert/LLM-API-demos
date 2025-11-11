# Structured Output Extraction: Comparative Study of LLM APIs

A comparative demonstration of structured output capabilities across three major LLM API providers: OpenAI, Google Gemini, and Anthropic Claude.

## Overview

This project demonstrates how different LLM APIs implement structured output generation using JSON Schema constraints. It extracts academic paper metadata from unstructured text, comparing the approaches and performance of:

- **OpenAI GPT-4o**: `response_format` with `json_schema` and `strict: true`
- **Google Gemini 2.5 Flash**: `response_mime_type: application/json` with `response_json_schema`  
- **Anthropic Claude Sonnet 4.5**: Tool use pattern with `input_schema` and `tool_choice`

## Features

- **Unified Schema Definition**: Single JSON Schema shared across all three providers
- **Strict Validation**: Enforces required fields, enum values, regex patterns, and null handling
- **Normalization Rules**: Consistent handling of venue names (e.g., NIPS → NeurIPS)
- **Robust Parsing**: Handles various response formats including markdown code fences
- **Rate Limit Management**: Automatic delays for providers with strict free-tier limits

## Schema Definition

The extraction schema defines the following fields:

**Required Fields:**
- `title`: Paper title (3-300 characters)
- `authors`: List of author names (≥1)
- `venue`: Conference/journal name (enumerated: NeurIPS, ICLR, ICML, ACL, CVPR, etc.)
- `year`: Publication year (1900-2100)
- `doi`: DOI string (pattern: `^10\..*`) or null
- `keywords`: 3-10 lowercase keywords (pattern: `^[a-z0-9\- ]+$`)

**Optional Fields (nullable):**
- `abstract`: Paper abstract (≥20 characters)
- `arxiv_id`: arXiv identifier (pattern: `^\d{4}\.\d{4,5}(v\d+)?$`)
- `url`: Paper URL

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Set up API keys (choose one method)

# Method 1: Environment variables
export OPENAI_API_KEY="sk-..."
export GEMINI_API_KEY="AIza..."  # or GOOGLE_API_KEY
export ANTHROPIC_API_KEY="sk-ant-..."

# Method 2: .env file
cat > .env << EOF
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=AIza...
ANTHROPIC_API_KEY=sk-ant-...
EOF
```

## Usage

### Run Individual Demos

```bash
# OpenAI demo
python openai_demo.py --file samples/paper.txt

# Google Gemini demo
python gemini_demo.py --file samples/paper.txt

# Anthropic Claude demo
python anthropic_demo.py --file samples/paper.txt
```

### Run All Demos

```bash
python run_all.py
```

This executes all three APIs sequentially on both sample files (`paper.txt` and `paper_noise.txt`) with automatic rate limiting for Gemini's free tier.

## API-Specific Implementation Notes

### OpenAI

- Uses `strict: True` mode requiring all properties in `required` array
- No optional fields allowed (use `anyOf` with `null` instead)
- Does not support `format: uri` validation
- Regex patterns must use double-escaped backslashes (e.g., `^10\\..+`)

### Google Gemini

- Free tier: 5 RPM, 1M TPM, 25 RPD (strictest limits)
- Supports both `GEMINI_API_KEY` (official) and `GOOGLE_API_KEY` (legacy)
- Response accessible via `resp.text` or by concatenating candidate parts
- May return 503 errors under heavy load (handled with automatic retries)

### Anthropic Claude

- Uses tool calling pattern instead of native JSON mode
- Requires explicit `tool_choice` to force tool usage
- Response parsed from `ToolUseBlock` in message content
- Most verbose token usage (~1700 tokens vs ~600-850 for others)

## Sample Data

- `samples/paper.txt`: Clean, well-formatted paper metadata
- `samples/paper_noise.txt`: Noisy text with formatting inconsistencies (tests robustness)

## Output

Extracted metadata is saved to `outputs/` as JSON files:
- `outputs/openai_{filename}.json`
- `outputs/gemini_{filename}.json`
- `outputs/anthropic_{filename}.json`

## Token Usage Comparison

Based on empirical tests with sample data:

| Provider | Model | Avg Tokens | Cost Efficiency |
|----------|-------|------------|----------------|
| OpenAI | gpt-4o-2024-08-06 | ~600 | Highest |
| Google Gemini | gemini-2.5-flash | ~850 | High |
| Anthropic | claude-sonnet-4-5 | ~1700 | Medium |

*Note: Anthropic's higher token count reflects tool use overhead*

## Rate Limits (Free Tier)

| Provider | RPM | TPM | RPD |
|----------|-----|-----|-----|
| OpenAI | 60 | 60K | 200 |
| Google Gemini | **5** | 1M | 25 |
| Anthropic | 50 | 40K | 1000 |

## Project Structure

```
01_structured_extract/
├── openai_demo.py          # OpenAI GPT-4o implementation
├── gemini_demo.py          # Google Gemini implementation
├── anthropic_demo.py       # Anthropic Claude implementation
├── run_all.py              # Sequential execution of all demos
├── requirements.txt        # Python dependencies
├── common/
│   ├── schema.py          # JSON Schema and system prompt
│   └── validate.py        # Validation and I/O utilities
├── samples/
│   ├── paper.txt          # Clean sample input
│   └── paper_noise.txt    # Noisy sample input
└── outputs/               # Generated JSON outputs (gitignored)
```

## Requirements

- Python 3.9+
- OpenAI Python SDK ≥1.45.0
- Anthropic Python SDK ≥0.34.0
- Google GenAI SDK ≥0.2.0
- jsonschema ≥4.22.0
- python-dotenv ≥1.0.1

## License

This project is intended for academic demonstration and research purposes.

## Citation

If you use this code in your research, please cite:

```bibtex
@misc{llm-structured-output-demo,
  title={Structured Output Extraction: Comparative Study of LLM APIs},
  author={Your Name},
  year={2025},
  howpublished={\url{https://github.com/yourusername/API_Demo}}
}
```

## Acknowledgments

This demonstration compares the structured output capabilities of:
- [OpenAI API](https://platform.openai.com/docs/guides/structured-outputs)
- [Google Gemini API](https://ai.google.dev/gemini-api/docs/json-mode)
- [Anthropic Claude API](https://docs.anthropic.com/en/docs/build-with-claude/tool-use)
