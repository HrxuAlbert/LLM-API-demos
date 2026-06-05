# LLM API Demos

This repository contains lightweight demos for structured LLM API usage, agent-oriented workflows, and research prototyping.

The goal of this repository is to collect small, reusable examples for experimenting with modern LLM APIs, including structured outputs, tool/function calling, prompt-based extraction, and early-stage agent workflow design.

## Research Context

This repository supports my broader research on trustworthy multi-agent AI systems and LLM-agent collaboration. In particular, these demos provide practical building blocks for:

* structured proposal generation;
* evidence-aware LLM outputs;
* agent response formatting;
* lightweight evaluation pipelines;
* API-based research prototyping.

It is not intended to be a full framework. Instead, it serves as a compact experimental space for testing API behaviors and implementation patterns that may later be integrated into larger research systems.

## Scope

Current and future examples may include:

* structured JSON output generation;
* function/tool calling demos;
* multi-agent interaction prototypes;
* claim verification or evidence-grounded response examples;
* prompt templates for research experiments;
* basic visualization or analysis utilities.


## 📋 Table of Contents

- [Overview](#overview)
- [Demos](#demos)
  - [1. Structured Data Extraction](#1-structured-data-extraction)
  - [2. Function Calling & Tool Use](#2-function-calling--tool-use)
  - [3. MARL Visualization](#3-marl-visualization)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [License](#license)
- [Contact](#contact)

---

## 🎯 Overview

This project demonstrates three core capabilities of modern LLM APIs:

1. **Structured Extraction**: Parse unstructured text into validated JSON schemas
2. **Function Calling**: Enable LLMs to interact with external tools and APIs
3. **Multi-Agent Systems**: Use LLMs for high-level coordination in MARL environments

Each demo is self-contained, well-documented, and includes practical examples.

---

## 🚀 Demos

### 1. Structured Data Extraction

**Directory**: `01_structured_extract/`

Extract structured metadata from academic papers using three major LLM providers:
- **OpenAI GPT-4**: Strict JSON schema enforcement
- **Anthropic Claude**: Tool-based extraction
- **Google Gemini**: JSON mode extraction

**Key Features**:
- JSON Schema validation with `jsonschema`
- API rate limiting handling
- Unified schema across providers
- Batch processing support

**Example**:
```bash
cd 01_structured_extract
python openai_demo.py samples/paper.txt
```

**Output**: Validated JSON with title, authors, venue, year, keywords, etc.

[📖 Detailed Documentation](01_structured_extract/README.md)

---

### 2. Function Calling & Tool Use

**Directory**: `02_tool_calling/`

An AI day planner that demonstrates LLM function calling with real-world APIs:
- **Weather API**: Fetch forecasts from Open-Meteo
- **Calendar API**: Find free slots and book meetings
- **Routing API**: Estimate travel time with OSRM

**Key Features**:
- OpenAI function calling with multiple tools
- File-based input/output for easy testing
- Batch processing of multiple requests
- Human-readable Markdown output

**Example**:
```bash
cd 02_tool_calling
python planner.py --request requests/example1_basic.txt
```

**Output**: Comprehensive daily plan with weather, meetings, and travel times.

[📖 Detailed Documentation](02_tool_calling/README.md)

---

### 3. MARL Visualization

**Directory**: `03_MARL_ViZ_Demo/`

API-first multi-agent reinforcement learning visualization without training:
- **High-level Director**: Greedy or LLM-based agent-landmark assignment
- **Low-level Actor**: HTTP policy server or local heuristics
- **Environments**: PettingZoo cooperative (spread) and adversarial (tag)

**Key Features**:
- Real-time GIF generation with English captions
- Dual-axis metrics plots (reward + coverage)
- Modular architecture (director + actor)
- No training required (demonstration only)

**Example**:
```bash
cd 03_MARL_ViZ_Demo
# Terminal 1: Start policy server (optional)
python src/policy_server.py

# Terminal 2: Run visualization
python src/marl_viz.py --env spread --steps 200 --director greedy --actor local
```

**Output**: 
- `outputs/rollout_*.gif`: 20-second animated visualization
- `outputs/metrics_*.png`: Performance charts

[📖 Detailed Documentation](03_MARL_ViZ_Demo/README.md)

---

## ⚡ Quick Start

### Prerequisites

- Python 3.11 or higher
- API keys (at least one):
  - OpenAI: [Get API key](https://platform.openai.com/api-keys)
  - Anthropic: [Get API key](https://console.anthropic.com/)
  - Google Gemini: [Get API key](https://makersuite.google.com/app/apikey)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/API_Demo.git
cd API_Demo

# Install all dependencies
pip install -r requirements.txt

# Set up API keys
echo "OPENAI_API_KEY=your_key_here" > .env
echo "ANTHROPIC_API_KEY=your_key_here" >> .env
echo "GEMINI_API_KEY=your_key_here" >> .env
```

### Run a Demo

```bash
# Demo 1: Structured extraction
cd 01_structured_extract
python run_all.py

# Demo 2: Function calling
cd ../02_tool_calling
python run_examples.py

# Demo 3: MARL visualization
cd ../03_MARL_ViZ_Demo
python src/marl_viz.py --env spread --steps 100 --director greedy
```

---

## 📁 Project Structure

```
API_Demo/
├── README.md                          # This file
├── requirements.txt                   # Unified dependencies
├── LICENSE                            # MIT License
├── .gitignore                        # Git ignore rules
│
├── 01_structured_extract/            # Demo 1: Structured Extraction
│   ├── README.md                     # Detailed documentation
│   ├── requirements.txt              # Local dependencies
│   ├── openai_demo.py               # OpenAI implementation
│   ├── anthropic_demo.py            # Anthropic implementation
│   ├── gemini_demo.py               # Google Gemini implementation
│   ├── run_all.py                   # Batch runner
│   ├── common/                       # Shared modules
│   │   ├── schema.py                # JSON schema definition
│   │   └── validate.py              # Validation utilities
│   └── samples/                      # Example inputs
│       ├── paper.txt
│       └── paper_noise.txt
│
├── 02_tool_calling/                  # Demo 2: Function Calling
│   ├── README.md                     # Detailed documentation
│   ├── DEMO_GUIDE.md                # Presentation guide
│   ├── requirements.txt              # Local dependencies
│   ├── planner.py                   # Main planner script
│   ├── run_examples.py              # Batch processor
│   ├── requests/                     # Example requests
│   │   ├── README.md
│   │   ├── example1_basic.txt
│   │   ├── example2_complex.txt
│   │   └── example3_weather_focused.txt
│   └── plans/                        # Output directory (generated)
│
└── 03_MARL_ViZ_Demo/                # Demo 3: MARL Visualization
    ├── README.md                     # Detailed documentation
    ├── DEMO_GUIDE.md                # Presentation guide
    ├── requirements.txt              # Local dependencies
    ├── src/
    │   ├── marl_viz.py              # Main visualization client
    │   ├── policy_server.py         # FastAPI policy server
    │   └── llm_director.py          # Assignment coordinator
    └── outputs/                      # Output directory (generated)
```

---

## 📦 Requirements

### Core Dependencies

All demos share these core dependencies:
- `openai>=1.0.0` - OpenAI API client
- `anthropic>=0.34.0` - Anthropic API client
- `google-generativeai>=0.3.0` - Google Gemini API client
- `python-dotenv>=1.0.0` - Environment variable management
- `requests>=2.32.0` - HTTP requests

### Demo-Specific Dependencies

**Demo 1 (Structured Extract)**:
- `jsonschema>=4.22.0` - JSON schema validation

**Demo 2 (Tool Calling)**:
- `python-dateutil>=2.8.0` - Date parsing

**Demo 3 (MARL Viz)**:
- `pettingzoo[mpe]>=1.24` - Multi-agent environments
- `gymnasium>=0.29` - RL environment framework
- `numpy>=1.26` - Numerical computing
- `imageio>=2.34` - GIF generation
- `pillow>=10.3` - Image processing
- `matplotlib>=3.8` - Plotting
- `fastapi>=0.115` - API server
- `uvicorn>=0.30` - ASGI server

### Installation Options

```bash
# Install all dependencies (recommended)
pip install -r requirements.txt

# Or install per demo
pip install -r 01_structured_extract/requirements.txt
pip install -r 02_tool_calling/requirements.txt
pip install -r 03_MARL_ViZ_Demo/requirements.txt
```

---

## 🔧 Configuration

### API Keys

Create a `.env` file in the project root or in each demo directory:

```bash
# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini  # Optional: override default model

# Anthropic
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-sonnet-4-5  # Optional

# Google Gemini
GEMINI_API_KEY=AI...
```

### Rate Limiting

- **Google Gemini Free Tier**: 5 RPM (handled automatically with delays)
- **OpenAI**: Depends on your tier
- **Anthropic**: Depends on your tier

---

## 🧪 Testing

Each demo includes test scripts:

```bash
# Demo 1: Test all three providers
cd 01_structured_extract
python run_all.py

# Demo 2: Test all example requests
cd 02_tool_calling
python run_examples.py

# Demo 3: Test both environments
cd 03_MARL_ViZ_Demo
python src/marl_viz.py --env spread --steps 50
python src/marl_viz.py --env tag --steps 50
```

---

## 🎓 Use Cases

### Academic Research
- Rapid prototyping of LLM-powered systems
- Benchmarking different API providers
- Teaching LLM application development

### Industry Applications
- Data extraction pipelines
- Intelligent assistants with tool use
- Multi-agent system coordination

### Education
- Hands-on LLM API tutorials
- Best practices for API integration
- Prompt engineering examples

---

## 🐛 Troubleshooting

### Common Issues

**Issue**: `ModuleNotFoundError`
- **Solution**: Install dependencies: `pip install -r requirements.txt`

**Issue**: API key not found
- **Solution**: Create `.env` file with your API keys

**Issue**: Rate limit errors (Google Gemini)
- **Solution**: Use free tier with built-in delays or upgrade plan

**Issue**: Import errors from `pettingzoo`
- **Solution**: Update imports (handled automatically in latest version)

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [OpenAI](https://openai.com/) for GPT-4 API
- [Anthropic](https://www.anthropic.com/) for Claude API
- [Google](https://ai.google.dev/) for Gemini API
- [PettingZoo](https://pettingzoo.farama.org/) for multi-agent environments
- [FastAPI](https://fastapi.tiangolo.com/) for the elegant web framework

---

## 📧 Contact

For questions or suggestions, please open an issue or contact [2614067X@student.gla.ac.uk](mailto:2614067X@student.gla.ac.uk).

---

**⭐ If you find this project useful, please consider giving it a star!**

