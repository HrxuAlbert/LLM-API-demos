# MARL API Visualization Demo

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **API-First Multi-Agent Reinforcement Learning Visualization Without Training**

This project demonstrates the role of APIs in Multi-Agent Reinforcement Learning (MARL) through an API-first architecture that decouples coordination, policy serving, and environment interaction.

## 📋 Overview

Modern MARL systems benefit from modular, service-oriented architectures. This demo showcases:

1. **High-Level Director**: Centralized coordination that assigns agents to landmarks using:
   - Greedy algorithm (minimum distance)
   - LLM-based reasoning (OpenAI GPT)

2. **Low-Level Policy Server**: HTTP API serving discrete actions via:
   - Random exploration
   - Goal-directed heuristics

3. **Visualization Client**: Connects to PettingZoo environments, queries policy APIs, and renders annotated episodes

### Key Features

- **No Training Required**: Demonstrates API architecture without RL training overhead
- **Pluggable Components**: Swap directors and actors via command-line flags
- **Rich Visualization**: Annotated GIFs with metrics and assignment rationale
- **Metrics Tracking**: Cumulative reward and coverage curves

## 🎯 Supported Environments

| Environment | Type | Agents | Description |
|------------|------|--------|-------------|
| `simple_spread_v3` | Cooperative | 3 | Agents must cover 3 landmarks |
| `simple_tag_v3` | Adversarial | 3 | Predators chase prey |

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- OpenAI API key (optional, for LLM-based director)

### Installation

```bash
# Clone and navigate to project
cd 03_MARL_ViZ_Demo

# Install dependencies
pip install -r requirements.txt

# (Optional) Set up OpenAI API key for LLM director
echo "OPENAI_API_KEY=your_key_here" > .env
```

### Running the Demo

#### Step 1: Start Policy Server

```bash
python src/policy_server.py --host 127.0.0.1 --port 8000
```

The server exposes two endpoints:
- `GET /health`: Health check
- `POST /act`: Action recommendation for agent observations

#### Step 2: Run Visualization Client

**Cooperative environment with greedy assignment + HTTP policy:**
```bash
python src/marl_viz.py \
  --env spread \
  --steps 80 \
  --director greedy \
  --actor http \
  --policy-url http://127.0.0.1:8000/act
```

**Cooperative environment with LLM assignment + local heuristics:**
```bash
python src/marl_viz.py \
  --env spread \
  --steps 80 \
  --director llm \
  --actor local
```

**Adversarial environment (no assignment needed):**
```bash
python src/marl_viz.py \
  --env tag \
  --steps 120 \
  --actor http \
  --policy-url http://127.0.0.1:8000/act
```

### Outputs

Generated files are saved in the `outputs/` directory:

1. **`rollout_*.gif`**: Annotated episode visualization with:
   - Episode objective
   - Current step and cumulative reward
   - Coverage percentage (spread) or team reward (tag)
   - Agent-landmark assignments (if director is used)

2. **`metrics_*.png`**: Plots showing:
   - Cumulative team reward over time
   - Coverage curve (spread environment only)

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Visualization Client                     │
│                      (marl_viz.py)                          │
│  • PettingZoo environment interaction                       │
│  • Frame rendering and annotation                           │
│  • Metrics collection and plotting                          │
└────────────┬────────────────────────────────┬───────────────┘
             │                                │
             │ HTTP POST /act                 │ Assignment logic
             │                                │
    ┌────────▼─────────┐            ┌────────▼──────────┐
    │  Policy Server   │            │  LLM Director     │
    │ (policy_server)  │            │ (llm_director)    │
    │                  │            │                   │
    │ • Random actions │            │ • Greedy algorithm│
    │ • Heuristics     │            │ • OpenAI GPT      │
    └──────────────────┘            └───────────────────┘
```

### Component Details

#### 1. `marl_viz.py` - Visualization Client

Core functionality:
- Environment initialization and reset
- Action querying (HTTP API or local heuristics)
- Episode execution and rendering
- Coverage estimation via pixel analysis
- GIF and metrics export

Key functions:
- `record_episode()`: Main orchestration loop
- `overlay()`: Caption rendering on frames
- `estimate_coverage()`: Landmark coverage calculation
- `discrete_move_towards()`: Local heuristic controller

#### 2. `policy_server.py` - Policy API Server

FastAPI server providing stateless action recommendations:
- **Random mode**: Exploration via uniform sampling
- **Goal-directed mode**: Heuristic navigation towards assigned landmark

#### 3. `llm_director.py` - High-Level Coordinator

Centralized planner for agent-landmark assignment:
- **Greedy algorithm**: Minimizes total distance using greedy matching
- **LLM-based**: Uses OpenAI GPT for reasoning-based assignment with fallback

## 🔧 Command-Line Options

### `marl_viz.py`

| Option | Choices/Type | Default | Description |
|--------|--------------|---------|-------------|
| `--env` | `spread`, `tag` | `spread` | Environment type |
| `--steps` | `int` | `80` | Maximum episode length |
| `--seed` | `int` | `7` | Random seed |
| `--fps` | `int` | `8` | GIF frame rate |
| `--out` | `str` | `outputs` | Output directory |
| `--director` | `none`, `greedy`, `llm` | `none` | Assignment strategy |
| `--actor` | `local`, `http` | `local` | Action source |
| `--policy-url` | `str` | `http://127.0.0.1:8000/act` | Policy server endpoint |

### `policy_server.py`

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--host` | `str` | `127.0.0.1` | Server host |
| `--port` | `int` | `8000` | Server port |

## 📊 Example Results

### Cooperative Environment (simple_spread_v3)

**Configuration**: 3 agents, 3 landmarks, greedy director, 80 steps

**Observed Behavior**:
- Greedy assignment minimizes initial total distance
- Agents navigate towards assigned landmarks using heuristics
- Coverage increases as agents reach targets
- Cumulative reward correlates with coverage improvement

**Sample Assignment**:
```
A0 → L2 (distance: 0.15)
A1 → L0 (distance: 0.23)
A2 → L1 (distance: 0.18)
```

### Adversarial Environment (simple_tag_v3)

**Configuration**: 2 predators, 1 prey, random policies, 120 steps

**Observed Behavior**:
- Predators explore randomly
- Prey evades via random walk
- Occasional captures lead to reward spikes
- No coordination between predators (baseline)

## 🧪 Extension Ideas

1. **Advanced Directors**:
   - Hungarian algorithm for optimal assignment
   - Decentralized assignment via auction mechanisms
   - Dynamic reassignment based on environment changes

2. **Learned Policies**:
   - Train RL policies and serve via policy server
   - A/B test different training algorithms
   - Multi-armed bandit for policy selection

3. **Additional Environments**:
   - Custom PettingZoo environments
   - Integration with other MARL frameworks (RLlib, PufferLib)

4. **Enhanced Visualization**:
   - Real-time web dashboard (Streamlit/Gradio)
   - 3D rendering for complex environments
   - Trajectory heatmaps and attention visualization

## 🔬 Research Applications

This demo is suitable for:
- **Teaching**: Introducing API-first MARL architecture to students
- **Prototyping**: Rapid iteration on coordination strategies
- **Benchmarking**: Comparing heuristic vs. learned policies
- **Ablation Studies**: Isolating effects of director vs. actor quality

## 📝 Citation

If you use this demo in your research or teaching, please cite:

```bibtex
@misc{marl_api_viz_demo,
  title={API-First Multi-Agent Reinforcement Learning Visualization},
  author={Your Name},
  year={2025},
  url={https://github.com/yourusername/API_Demo}
}
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.

## 🙏 Acknowledgments

- [PettingZoo](https://pettingzoo.farama.org/) for multi-agent environments
- [FastAPI](https://fastapi.tiangolo.com/) for elegant API framework
- [OpenAI](https://openai.com/) for LLM-based reasoning

## 🐛 Troubleshooting

### Common Issues

**Issue**: `ModuleNotFoundError: No module named 'pettingzoo'`
- **Solution**: Install dependencies: `pip install -r requirements.txt`

**Issue**: Policy server connection timeout
- **Solution**: Ensure server is running on specified host/port: `curl http://127.0.0.1:8000/health`

**Issue**: LLM director fallback to greedy
- **Solution**: Check `OPENAI_API_KEY` in `.env` and verify API quota

**Issue**: Blank or corrupted GIF output
- **Solution**: Check environment rendering mode is `rgb_array` and `imageio` is properly installed

**Issue**: Coverage always shows 0%
- **Solution**: Verify landmark colors in environment and adjust thresholds in `estimate_coverage()`

## 📧 Contact

For questions or suggestions, please open an issue or contact [your.email@example.com](mailto:your.email@example.com).

---

**Made with ❤️ for the MARL community**
