# Demo Guide - Function Calling Planner

Quick guide for presenting this demo effectively.

## Pre-Demo Setup

```bash
# 1. Install dependencies (if not already done)
pip install -r requirements.txt

# 2. Set API key
export OPENAI_API_KEY="your-key-here"

# 3. Navigate to demo directory
cd 02_tool_calling
```

## Demo Flow

### Part 1: Show Input Files (30 seconds)

```bash
# Show available request examples
ls -1 requests/*.txt
```

**Say**: "I've prepared several planning scenarios as text files. Let's look at one."

```bash
cat requests/example1_basic.txt
```

### Part 2: Run Single Example (2-3 minutes)

```bash
python planner.py --request requests/example1_basic.txt
```

**Highlight**:
- AI autonomously decides which tools to call
- Real-time weather data from Open-Meteo API
- Route planning via OSRM
- Calendar slot finding and booking
- Human-readable final output

### Part 3: Show Generated Output (30 seconds)

```bash
# List generated plans
ls -lh plans/

# Show the plan file
cat plans/plan_example1_basic_*.md
```

**Say**: "The plan is automatically saved as Markdown, perfect for sharing or documentation."

### Part 4: Batch Processing (Optional, 1 minute)

```bash
python run_examples.py
```

**Say**: "We can also process multiple scenarios at once to compare how the AI handles different situations."

## Key Talking Points

### Technical Highlights

1. **Function Calling API**
   - LLM decides autonomously which tools to use
   - Can make multiple sequential calls
   - Builds context across calls

2. **Real External APIs**
   - Open-Meteo: Live weather data (no key required)
   - OSRM: Route planning (free, open source)
   - Both are production-ready APIs

3. **Input/Output Files**
   - Inputs: Plain text requests (easy to prepare)
   - Outputs: Markdown files (easy to share)
   - Perfect for comparing scenarios

### Demo Advantages

- ✅ **Reproducible**: Save inputs for consistent demos
- ✅ **Flexible**: Easy to create new scenarios
- ✅ **Professional**: Polished output files
- ✅ **Comparative**: Run multiple scenarios

## Common Questions & Answers

**Q: How does it decide which tools to call?**
A: The LLM analyzes the request and autonomously selects appropriate tools based on function descriptions. It can chain multiple calls to gather all needed information.

**Q: Can it handle failures?**
A: Yes - OSRM fallback uses geometric calculations if the routing service is unavailable. Weather API is generally reliable with no authentication required.

**Q: How accurate is the output?**
A: Weather and routing use real APIs with live data. Calendar is simulated (hardcoded busy slots) but demonstrates the pattern for real calendar integration.

**Q: Can I add custom locations?**
A: Yes - modify the HOME and OFFICE dictionaries in planner.py, or add new locations with lat/lon coordinates.

## Customization for Your Demo

### Add Your Own Request

Create `requests/my_scenario.txt`:
```
Plan my workshop day tomorrow:
- 09:00-12:00: Deep work session
- Need 1 hour lunch break
- Afternoon: Schedule 45-min team sync
- Check weather for outdoor lunch options
```

Then run:
```bash
python planner.py --request requests/my_scenario.txt
```

### Modify Demo Data

Edit `planner.py`:
- Lines 16-18: HOME, OFFICE locations
- Lines 25-33: Simulated busy time slots
- Line 13: Timezone

## Troubleshooting

### API Rate Limits
If you hit rate limits:
- OpenAI free tier: 60 RPM
- Add delays between runs: `sleep 5 && python planner.py ...`

### No Weather Data
If weather API fails:
- Check internet connection
- Verify coordinates are valid (lat/lon)
- Open-Meteo might be temporarily down (rare)

### Missing Dependencies
```bash
pip install -r requirements.txt
```

## After Demo

Show the generated files structure:
```bash
tree -L 2
# or
find . -type f -not -path '*/.*' | sort
```

Point audience to:
- README.md for complete documentation
- requests/ for example inputs
- plans/ for generated outputs
- GitHub repo (if public)

## Time Estimates

- **Quick demo**: 3-4 minutes (single example)
- **Full demo**: 8-10 minutes (with batch processing)
- **Deep dive**: 15-20 minutes (with code walkthrough)

## Success Metrics

After demo, audience should understand:
- ✅ Function calling enables AI autonomy
- ✅ Real APIs can be integrated seamlessly
- ✅ File-based I/O makes demos reproducible
- ✅ Output is production-ready (Markdown plans)

