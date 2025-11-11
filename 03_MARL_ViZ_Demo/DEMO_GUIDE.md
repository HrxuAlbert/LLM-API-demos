# Demo Guide for MARL API Visualization

This guide provides step-by-step instructions for demonstrating the MARL API visualization system.

## 🎯 Demo Scenarios

### Scenario 1: Basic Cooperative with Local Heuristics

**Goal**: Show how agents can cover landmarks without training using simple heuristics.

**Steps**:
```bash
# Run with greedy assignment and local heuristics
python src/marl_viz.py --env spread --steps 80 --director greedy --actor local --seed 7
```

**Expected Output**:
- GIF showing 3 agents moving towards assigned landmarks
- Assignment visible in caption: "A0→L2, A1→L0, A2→L1"
- Coverage increasing from ~0% to ~80%+
- Metrics plot showing reward and coverage curves

**Key Points**:
- No training required
- Greedy assignment minimizes initial total distance
- Heuristic controller is simple but effective

---

### Scenario 2: API-First Architecture with Policy Server

**Goal**: Demonstrate decoupled architecture with HTTP policy serving.

**Steps**:
```bash
# Terminal 1: Start policy server
python src/policy_server.py --host 127.0.0.1 --port 8000

# Terminal 2: Run client connecting to server
python src/marl_viz.py --env spread --steps 80 --director greedy --actor http --policy-url http://127.0.0.1:8000/act
```

**Expected Output**:
- Policy server logs showing incoming requests
- Client behavior identical to Scenario 1
- Demonstrates API modularity

**Key Points**:
- Client and policy are decoupled via HTTP
- Easy to swap policy implementations
- Server can handle multiple clients

---

### Scenario 3: LLM-Based Assignment (Requires OpenAI API Key)

**Goal**: Show LLM reasoning for agent-landmark assignment.

**Prerequisites**:
```bash
# Set up API key
export OPENAI_API_KEY="your_key_here"
# Or create .env file:
# echo "OPENAI_API_KEY=your_key_here" > .env
```

**Steps**:
```bash
python src/marl_viz.py --env spread --steps 80 --director llm --actor local --seed 7
```

**Expected Output**:
- LLM generates assignment with rationale
- Rationale visible in GIF caption
- Similar or better assignment compared to greedy

**Key Points**:
- LLM can reason about spatial relationships
- Fallback to greedy if API fails
- Example of integrating LLM into MARL

---

### Scenario 4: Adversarial Environment

**Goal**: Demonstrate adversarial multi-agent dynamics.

**Steps**:
```bash
python src/marl_viz.py --env tag --steps 120 --actor local --seed 42
```

**Expected Output**:
- 2 predators chasing 1 prey
- Random policies (no coordination)
- Sparse rewards when prey is caught
- No assignment (adversarial setting)

**Key Points**:
- Different environment type
- No cooperation needed
- Baseline for comparing learned policies

---

## 🔍 What to Look For

### In the GIF Output

1. **Agent Movement**: Smooth navigation towards targets
2. **Assignment Display**: Clear mapping (A0→L2, etc.)
3. **Coverage Evolution**: Percentage increasing over time
4. **Rationale**: Why this assignment was chosen

### In the Metrics Plot

1. **Reward Curve**: Should be mostly increasing
2. **Coverage Curve** (spread only): Should reach 70-90%
3. **Plateaus**: When agents reach targets
4. **Variance**: Different seeds produce different trajectories

---

## 🐛 Troubleshooting During Demo

### Server Won't Start
```bash
# Check if port is in use
lsof -i :8000

# Kill process if needed
kill -9 <PID>
```

### Client Can't Connect to Server
```bash
# Verify server is running
curl http://127.0.0.1:8000/health

# Expected: {"ok":true,"status":"healthy"}
```

### No GIF Generated
```bash
# Check outputs directory
ls -l outputs/

# Verify no errors in terminal output
# Check imageio installation: pip list | grep imageio
```

### LLM Assignment Not Working
```bash
# Verify API key is set
echo $OPENAI_API_KEY

# Check for API errors in terminal output
# Fallback to greedy should still work
```

---

## 📊 Comparing Results

### Different Seeds
```bash
# Run with different seeds to show stochasticity
python src/marl_viz.py --env spread --director greedy --actor local --seed 1
python src/marl_viz.py --env spread --director greedy --actor local --seed 42
python src/marl_viz.py --env spread --director greedy --actor local --seed 123
```

### Different Directors
```bash
# No assignment (random)
python src/marl_viz.py --env spread --director none --actor local

# Greedy assignment
python src/marl_viz.py --env spread --director greedy --actor local

# LLM assignment
python src/marl_viz.py --env spread --director llm --actor local
```

### Different Actors
```bash
# Local heuristics
python src/marl_viz.py --env spread --director greedy --actor local

# HTTP policy server
python src/marl_viz.py --env spread --director greedy --actor http
```

---

## 🎓 Teaching Points

1. **API-First Design**: Policies as microservices enable modularity
2. **Hierarchical Control**: Director (coordination) + Actor (execution)
3. **Heuristics vs Learning**: Simple rules can be effective for demos
4. **LLM Integration**: GPT can reason about spatial problems
5. **Visualization**: Critical for understanding multi-agent behavior

---

## 📈 Expected Performance

| Scenario | Final Coverage | Avg Reward | Steps to Converge |
|----------|---------------|------------|-------------------|
| No assignment | 30-50% | -15 to -5 | N/A (random) |
| Greedy | 75-90% | -5 to +5 | 40-60 |
| LLM | 75-90% | -5 to +5 | 40-60 |
| Tag (adversarial) | N/A | -10 to +10 | N/A (sparse) |

---

## 🚀 Advanced Demos

### Batch Processing
```bash
# Generate results for multiple seeds
for seed in 1 2 3 4 5; do
    python src/marl_viz.py --env spread --director greedy --actor local --seed $seed
done
```

### Custom Experiment
```bash
# Compare all director modes
python src/marl_viz.py --env spread --director none --seed 7
python src/marl_viz.py --env spread --director greedy --seed 7
python src/marl_viz.py --env spread --director llm --seed 7

# Compare output GIFs side-by-side
```

---

## 📝 Demo Script Template

```
1. Introduction (2 min)
   - Problem: Multi-agent coordination
   - Solution: API-first architecture

2. Architecture Overview (3 min)
   - Show diagram in README
   - Explain components

3. Live Demo 1: Greedy + Local (5 min)
   - Run Scenario 1
   - Show GIF and metrics
   - Explain heuristic

4. Live Demo 2: API Server (5 min)
   - Start server (Terminal 1)
   - Run client (Terminal 2)
   - Show server logs

5. Live Demo 3: LLM Director (5 min)
   - Run Scenario 3
   - Discuss LLM rationale
   - Compare with greedy

6. Q&A and Extensions (5 min)
   - Discuss research applications
   - Extension ideas
```

Total: ~25 minutes

---

**Good luck with your demo!** 🎉

