# Function Calling: Intelligent Day Planner

A demonstration of OpenAI's function calling API for building an intelligent day planning assistant that can autonomously gather information and make decisions.

## Overview

This demo showcases how LLMs can use function calling to interact with external tools and APIs, making them capable of:
- Fetching real-time weather data
- Estimating travel times between locations
- Finding free calendar slots across multiple attendees
- Booking meetings automatically

The planner operates autonomously, calling tools iteratively until it has enough information to produce a comprehensive daily plan.

## Features

### 🌤️ Weather Integration
- Uses [Open-Meteo API](https://open-meteo.com/) (free, no key required)
- Fetches daily forecasts and hourly precipitation data
- Recommends commute times based on weather conditions

### 🚗 Travel Time Estimation
- Primary: [OSRM](http://project-osrm.org/) routing service (free, open source)
- Fallback: Haversine distance calculation with mode-specific speeds
- Peak hour traffic adjustments for motorized transport
- Supports: walk, bike, transit, drive

### 📅 Calendar Management
- Finds common free slots across multiple attendees
- 15-minute time slot granularity
- Handles busy period merging and conflict resolution
- Idempotent event booking (prevents duplicates)

### 🤖 Autonomous Planning
- Iterative tool calling (up to 8 rounds)
- Context-aware decision making
- Generates human-readable daily schedules
- Handles edge cases (no free slots, bad weather, etc.)

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Set up OpenAI API key
export OPENAI_API_KEY="sk-..."

# Or use .env file
echo "OPENAI_API_KEY=sk-..." > .env
```

## Usage

### Quick Start

```bash
# Run with default example
python planner.py

# Use a specific request file
python planner.py --request requests/example1_basic.txt

# Provide inline prompt
python planner.py --prompt "Plan my day: morning meeting at 9am, lunch at noon"

# Run all examples in batch
python run_examples.py
```

### Input Options

The planner supports three input methods:

#### 1. Request Files (Recommended for demos)
```bash
python planner.py --request requests/example1_basic.txt
```

Create `.txt` files in `requests/` directory with your planning instructions. Benefits:
- ✅ Easy to prepare multiple scenarios
- ✅ Compare different inputs and outputs
- ✅ Perfect for demonstrations
- ✅ Output files auto-named with request filename

See [`requests/README.md`](requests/README.md) for examples and tips.

#### 2. Command-Line Prompt
```bash
python planner.py --prompt "Plan tomorrow: 9am standup, lunch with Sarah"
```

#### 3. Default Example
```bash
python planner.py  # Uses built-in example
```

### Output

Each run generates:
1. **Terminal output** - Interactive display of tool calls and final plan
2. **Markdown file** - Saved to `plans/` directory
   - With request file: `plan_[request-name]_[timestamp].md`
   - Without: `plan_[timestamp].md`

### Batch Processing

Process multiple requests at once for comparison:

```bash
python run_examples.py
```

This will:
1. Find all `.txt` files in `requests/` directory
2. Process each request sequentially
3. Generate individual plan files for each
4. Provide a summary of results

Perfect for:
- Comparing different planning scenarios
- Testing various prompts
- Generating multiple demo outputs
- Evaluating planner behavior across inputs

### Creating Custom Requests

Create a new `.txt` file in `requests/` directory:

```txt
Plan my day for tomorrow:
- Morning: team standup at 09:00 (15 min)
- Lunch: meet Sarah at 12:30-13:30
- Afternoon: prepare presentation (2 hours needed)
- Evening: gym session if weather is good
```

Then run:
```bash
python planner.py --request requests/your_request.txt
```

## How It Works

### 1. Tool Definitions

Four tools are available to the LLM:

```python
fetch_weather(date, lat, lon)          # Weather forecast
estimate_travel(origin, dest, mode, departure_iso)  # Travel time
find_free_slots(date, window_start, window_end, duration_minutes, attendees)  # Calendar
book_event(start_iso, duration_minutes, title, attendees, location)  # Booking
```

### 2. Planning Loop

```
User Request → LLM → Tool Calls → Tool Results → LLM → ... → Final Plan
```

The LLM autonomously decides:
- Which tools to call
- What arguments to use
- When it has enough information
- How to present the final plan

### 3. Output Format

The system generates a structured daily plan with:
- Executive summary
- Timeline with specific times
- Travel considerations
- Weather warnings
- Meeting confirmations

## Example Output

### Terminal Output

```
============================================================
DAILY PLAN
============================================================

Here's your plan for 2025-11-12:

SUMMARY:
Good news - the weather looks favorable with only a 15% chance of rain
and temperatures between 8-12°C. I've scheduled your FBA sync meeting
with Koust at 14:30-15:00 and planned your commute to avoid the busiest
times.

TIMELINE:
• 08:00 - Depart Home for Office
  └─ 12-minute walk (0.9km) - pleasant weather, no rain expected
  
• 08:15 - Arrive at Office
  └─ Start your workday

• 14:30-15:00 - FBA Sync Meeting
  └─ With: Koust
  └─ Status: ✓ Booked (ID: a4f2b8c9d1e3)

WEATHER NOTES:
- Morning: Dry and cool (8-10°C)
- Afternoon: Light clouds, 15% rain probability
- Recommendation: No umbrella needed

BOOKINGS CREATED:
✓ 1 event added to calendar
============================================================

✓ Plan saved to: plans/plan_20251111_145555.md
```

### Saved Markdown File

Each plan is saved with:
- **Timestamp** for easy identification
- **Request filename** (if using `--request`) for easy matching
- **Original request** for context
- **Complete plan** with all details
- **Professional formatting** ready for presentation

Example filenames:
- `plans/plan_example1_basic_20251111_150103.md` (from request file)
- `plans/plan_20251111_145555.md` (from command line)

This makes it perfect for:
- 📊 Demo presentations - prepare multiple scenarios
- 🔄 Scenario comparison - try different inputs
- 📧 Sharing via email - send polished plans
- 📝 Documentation - keep planning records
- 🧪 Testing - evaluate planner behavior

### File Structure

```
02_tool_calling/
├── requests/           # Input: Planning requests
│   ├── example1_basic.txt
│   ├── example2_complex.txt
│   ├── example3_weather_focused.txt
│   └── README.md
│
├── plans/             # Output: Generated plans
│   ├── plan_example1_basic_20251111_150103.md
│   ├── plan_example2_complex_20251111_150245.md
│   └── README.md
│
├── planner.py         # Main planner
├── run_examples.py    # Batch processor
└── README.md
```

## Architecture

### Tool Execution Flow

```python
def run(user_prompt):
    for iteration in range(8):
        response = openai.chat.completions.create(
            model="gpt-4o-2024-08-06",
            messages=messages,
            tools=tool_specs,
            tool_choice="auto"
        )
        
        if response.message.tool_calls:
            # Execute requested tools
            for tool_call in response.message.tool_calls:
                result = exec_tool(tool_call.function.name, 
                                   tool_call.function.arguments)
                # Feed results back to LLM
                messages.append(tool_result)
        else:
            # LLM has final answer
            return response.message.content
```

### Function Calling Schema Example

```json
{
  "type": "function",
  "function": {
    "name": "fetch_weather",
    "description": "Get daily weather forecast and hourly precipitation",
    "parameters": {
      "type": "object",
      "properties": {
        "date": {"type": "string", "pattern": "^\\d{4}-\\d{2}-\\d{2}$"},
        "lat": {"type": "number"},
        "lon": {"type": "number"}
      },
      "required": ["date", "lat", "lon"]
    }
  }
}
```

## Configuration

### Demo Data (planner.py)

```python
# Locations (Glasgow, UK)
HOME = {"name": "Home", "lat": 55.8642, "lon": -4.2518}
OFFICE = {"name": "Office", "lat": 55.8721, "lon": -4.2885}

# Attendees
ATTENDEES = ["haoran@lab", "koust@lab"]

# Busy time slots (simulated calendar)
BUSY = {
    "haoran@lab": {
        "2025-11-12": [["09:30","10:30"], ["12:00","13:00"]]
    },
    "koust@lab": {
        "2025-11-12": [["10:00","11:00"], ["16:00","17:00"]]
    }
}
```

### Environment Variables

```bash
OPENAI_API_KEY=sk-...           # Required
OPENAI_MODEL=gpt-4o-2024-08-06  # Optional (default shown)
```

## Technical Details

### API Services Used

| Service | Purpose | Cost | Authentication |
|---------|---------|------|----------------|
| OpenAI GPT-4o | Function calling LLM | Paid | API key required |
| Open-Meteo | Weather data | Free | No key |
| OSRM | Route planning | Free | No key |

### Rate Limits

- OpenAI: 60 RPM (free tier)
- Open-Meteo: No strict limits
- OSRM: Fair use policy

### Data Storage

- **Bookings**: Saved to `bookings.json` (local file)
- **Plans**: Saved to `plans/plan_TIMESTAMP.md` (Markdown format)
- In production: integrate with Google Calendar, Outlook, etc.

### Output Files

The planner generates two types of output files:

1. **Daily Plans** (`plans/*.md`)
   - Human-readable Markdown format
   - Includes timestamp and original request
   - Perfect for demo presentations
   - Auto-generated with each run

2. **Meeting Bookings** (`bookings.json`)
   - Machine-readable JSON format
   - Stores all booked events
   - Idempotent (no duplicates)

## Extending the Demo

### Add New Tools

```python
def search_restaurants(location: str, cuisine: str) -> dict:
    """Search for nearby restaurants."""
    # Implementation here
    return {"restaurants": [...]}

# Add to tool specs
{
    "type": "function",
    "function": {
        "name": "search_restaurants",
        "description": "Find restaurants near a location",
        "parameters": {...}
    }
}

# Add to dispatcher
elif name == "search_restaurants":
    res = search_restaurants(**args)
```

### Integrate Real Calendar APIs

```python
# Replace BUSY dict with:
def get_busy_slots(email: str, date: str):
    # Call Google Calendar API / Microsoft Graph API
    return calendar_api.get_events(email, date)
```

## Limitations

- Simulated calendar data (not connected to real calendar)
- Local file storage for bookings
- Demo locations hardcoded (Glasgow, UK)
- Single timezone support (Europe/London)
- No authentication or multi-user support

## License

MIT License - See LICENSE file for details.

## Acknowledgments

- [OpenAI Function Calling](https://platform.openai.com/docs/guides/function-calling)
- [Open-Meteo Weather API](https://open-meteo.com/)
- [OSRM Routing Engine](http://project-osrm.org/)

