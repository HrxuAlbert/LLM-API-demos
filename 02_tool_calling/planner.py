"""
Day Planner with Function Calling

A demonstration of OpenAI's function calling API for intelligent day planning.
Features: weather checking, travel time estimation, calendar slot finding, and event booking.
"""
import os, json, math, requests
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from openai import OpenAI

TZ = ZoneInfo("Europe/London")
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-2024-08-06")

# Demo data (locations in Glasgow, UK)
HOME = {"name": "Home", "lat": 55.8642, "lon": -4.2518}
OFFICE = {"name": "Office", "lat": 55.8721, "lon": -4.2885}
ATTENDEES = ["haoran@lab", "koust@lab"]

# Helper function to get tomorrow's date
def tomorrow():
    """Get tomorrow's date in YYYY-MM-DD format."""
    return (datetime.now(TZ) + timedelta(days=1)).date().strftime("%Y-%m-%d")

# Simulated busy time slots (in production, this would come from a calendar API)
BUSY = {
    "haoran@lab": {
        tomorrow(): [["09:30","10:30"], ["12:00","13:00"], ["15:00","15:30"]]
    },
    "koust@lab": {
        tomorrow(): [["10:00","11:00"], ["12:30","13:30"], ["16:00","17:00"]]
    }
}

# Local storage for bookings and plans
BOOKINGS_PATH = "bookings.json"
PLANS_DIR = "plans"

if not os.path.exists(BOOKINGS_PATH):
    with open(BOOKINGS_PATH, "w", encoding="utf-8") as f:
        json.dump([], f, indent=2)

# Create plans directory
os.makedirs(PLANS_DIR, exist_ok=True)

# ========== Tool Implementation: Weather Forecast ==========
def fetch_weather(date_str: str, lat: float, lon: float):
    """
    Fetch weather forecast using Open-Meteo API (free, no key required).
    
    Returns daily summary and hourly precipitation for 08:00-20:00.
    """
    url = ("https://api.open-meteo.com/v1/forecast"
           f"?latitude={lat}&longitude={lon}"
           "&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_mean"
           "&hourly=precipitation"
           "&timezone=Europe%2FLondon"
           f"&start_date={date_str}&end_date={date_str}")
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    js = r.json()
    d = js["daily"]
    min_t = float(d["temperature_2m_min"][0])
    max_t = float(d["temperature_2m_max"][0])
    rain_prob = float(d["precipitation_probability_mean"][0])
    
    # Extract hourly precipitation for 08:00-20:00
    hourly = js.get("hourly", {})
    times = hourly.get("time", [])
    precs = hourly.get("precipitation", [])
    hourly_precip = []
    for t, mm in zip(times, precs):
        hh = int(t[11:13]) if len(t) >= 13 else -1
        if 8 <= hh <= 20:
            hourly_precip.append({"time": t, "mm": float(mm)})
    
    # Generate weather summary
    summary = "dry and cool"
    if rain_prob > 45: summary = "light showers likely"
    if rain_prob > 60: summary = "periods of rain"
    
    return {
        "date": date_str,
        "summary": summary,
        "min_temp_c": min_t,
        "max_temp_c": max_t,
        "rain_prob": rain_prob,
        "hourly_precip": hourly_precip,
    }

# ========== Tool Implementation: Travel Time Estimation ==========
def haversine_km(lat1, lon1, lat2, lon2):
    """Calculate great-circle distance between two points using Haversine formula."""
    R = 6371.0  # Earth radius in kilometers
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*R*math.asin(math.sqrt(a))

def estimate_travel(origin, destination, mode: str, departure_iso: str):
    """
    Estimate travel time between two locations.
    
    First attempts to use OSRM API (free, no key). If fails, falls back to
    simple speed-based estimation with peak hour adjustments.
    """
    # Try OSRM routing service (free, no API key required)
    try:
        profile = "foot" if mode == "walk" else "driving"
        url = ("https://router.project-osrm.org/route/v1/"
               f"{profile}/{origin['lon']},{origin['lat']};{destination['lon']},{destination['lat']}?overview=false")
        r = requests.get(url, timeout=8)
        r.raise_for_status()
        js = r.json()
        secs = js["routes"][0]["duration"]
        km = js["routes"][0]["distance"] / 1000.0
        return {"minutes": round(secs/60.0,1), "distance_km": round(km,2), "source":"osrm"}
    except Exception:
        # Fallback: simple speed-based estimation
        speed_kmh = {"walk": 4.5, "bike": 15.0, "drive": 28.0, "transit": 22.0}.get(mode, 20.0)
        km = haversine_km(origin["lat"], origin["lon"], destination["lat"], destination["lon"])
        mins = km / speed_kmh * 60 + 5  # Add 5 min buffer
        
        # Apply peak hour multiplier for motorized transport
        hh = int(departure_iso[11:13]) if len(departure_iso) >= 13 else 9
        peak_multiplier = 1.25 if mode in ("drive","transit") and (7<=hh<=9 or 16<=hh<=18) else 1.0
        return {"minutes": round(mins*peak_multiplier,1), "distance_km": round(km,2), "source":"fallback"}

# ========== Tool Implementation: Calendar Slot Finding ==========
def _to_min(hhmm: str) -> int:
    """Convert HH:MM time string to minutes since midnight."""
    hh, mm = map(int, hhmm.split(":"))
    return hh*60 + mm

def find_free_slots(date_str: str, window_start: str, window_end: str, duration_minutes: int, attendees: list[str]):
    """
    Find common free time slots for all attendees within a time window.
    
    Returns slots in 15-minute increments that can accommodate the requested duration.
    """
    ws, we = _to_min(window_start), _to_min(window_end)
    
    # Collect all busy periods
    busy = []
    for a in attendees:
        for s,e in BUSY.get(a, {}).get(date_str, []):
            busy.append([_to_min(s), _to_min(e)])
    
    # Merge overlapping busy periods
    busy.sort()
    merged = []
    for s,e in busy:
        if not merged or s > merged[-1][1]:
            merged.append([s,e])
        else:
            merged[-1][1] = max(merged[-1][1], e)
    
    # Calculate free periods
    cur = ws
    free = []
    for s,e in merged:
        if s > cur: 
            free.append([cur, min(s,we)])
        cur = max(cur, e)
        if cur >= we: 
            break
    if cur < we: 
        free.append([cur,we])
    
    # Generate slot candidates in 15-minute increments
    out = []
    for s,e in free:
        t = s
        while t + duration_minutes <= e:
            hh, mm = divmod(t,60)
            iso = f"{date_str}T{hh:02d}:{mm:02d}:00+00:00"
            out.append(iso)
            t += 15  # 15-minute granularity
    
    return {"slots": out}

# ========== Tool Implementation: Event Booking ==========
def book_event(start_iso: str, duration_minutes: int, title: str, attendees: list[str], location: str|None=None):
    """
    Book a meeting event (idempotent based on content hash).
    
    Saves to local JSON file. In production, this would call a calendar API.
    """
    try:
        from dateutil.parser import isoparse
    except ImportError:
        raise ImportError("python-dateutil is required. Install with: pip install python-dateutil")
    
    end = isoparse(start_iso).astimezone(TZ) + timedelta(minutes=duration_minutes)
    event = {
        "meeting_id": str(abs(hash((start_iso,duration_minutes,title,tuple(sorted(attendees)),location))))[:12],
        "start_iso": start_iso,
        "end_iso": end.isoformat(),
        "title": title,
        "attendees": attendees,
        "location": location,
    }
    
    # Load existing bookings
    with open(BOOKINGS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Add if not duplicate
    if not any(x["meeting_id"] == event["meeting_id"] for x in data):
        data.append(event)
        with open(BOOKINGS_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    return event

# ========== OpenAI Function Calling Specifications ==========
def openai_tools_spec():
    """Define function calling schemas for OpenAI API."""
    return [
        {"type":"function","function":{
            "name":"fetch_weather",
            "description":"Get daily weather forecast and hourly precipitation for a specific date and location.",
            "parameters":{
                "type":"object",
                "properties":{
                    "date_str":{"type":"string","pattern":"^\\d{4}-\\d{2}-\\d{2}$","description":"Date in YYYY-MM-DD format"},
                    "lat":{"type":"number","description":"Latitude"},
                    "lon":{"type":"number","description":"Longitude"}
                },
                "required":["date_str","lat","lon"],"additionalProperties":False
            }
        }},
        {"type":"function","function":{
            "name":"estimate_travel",
            "description":"Estimate travel minutes between origin and destination for a mode.",
            "parameters":{
                "type":"object","properties":{
                    "origin":{"type":"object","properties":{"name":{"type":"string"},"lat":{"type":"number"},"lon":{"type":"number"}}, "required":["name","lat","lon"]},
                    "destination":{"type":"object","properties":{"name":{"type":"string"},"lat":{"type":"number"},"lon":{"type":"number"}}, "required":["name","lat","lon"]},
                    "mode":{"type":"string","enum":["walk","bike","transit","drive"]},
                    "departure_iso":{"type":"string"}
                },
                "required":["origin","destination","mode","departure_iso"],"additionalProperties":False
            }
        }},
        {"type":"function","function":{
            "name":"find_free_slots",
            "description":"Find common free 30-min slots within a window across attendees.",
            "parameters":{
                "type":"object","properties":{
                    "date_str":{"type":"string","pattern":"^\\d{4}-\\d{2}-\\d{2}$","description":"Date in YYYY-MM-DD format"},
                    "window_start":{"type":"string","pattern":"^\\d{2}:\\d{2}$","description":"Start time in HH:MM format"},
                    "window_end":{"type":"string","pattern":"^\\d{2}:\\d{2}$","description":"End time in HH:MM format"},
                    "duration_minutes":{"type":"integer","minimum":15,"maximum":180,"description":"Meeting duration in minutes"},
                    "attendees":{"type":"array","items":{"type":"string"},"description":"List of attendee email addresses"}
                },
                "required":["date_str","window_start","window_end","duration_minutes","attendees"],"additionalProperties":False
            }
        }},
        {"type":"function","function":{
            "name":"book_event",
            "description":"Create a meeting (idempotent).",
            "parameters":{
                "type":"object","properties":{
                    "start_iso":{"type":"string"},
                    "duration_minutes":{"type":"integer","minimum":15,"maximum":360},
                    "title":{"type":"string"},
                    "attendees":{"type":"array","items":{"type":"string"}},
                    "location":{"type":["string","null"]}
                },
                "required":["start_iso","duration_minutes","title","attendees"],"additionalProperties":False
            }
        }},
    ]

# ========== Tool Execution Dispatcher ==========
def exec_tool(name, args):
    """Execute a tool function and return its result."""
    print(f"\n[TOOL CALL] {name}")
    print(f"Arguments: {json.dumps(args, indent=2, ensure_ascii=False)}")
    
    try:
        if name == "fetch_weather":
            res = fetch_weather(**args)
        elif name == "estimate_travel":
            res = estimate_travel(**args)
        elif name == "find_free_slots":
            res = find_free_slots(**args)
        elif name == "book_event":
            res = book_event(**args)
        else:
            res = {"error": f"Unknown tool: {name}"}
    except Exception as e:
        res = {"error": f"{type(e).__name__}: {str(e)}"}
    
    print(f"[TOOL RESULT]")
    print(json.dumps(res, indent=2, ensure_ascii=False))
    return res

# ========== Output Management ==========
def save_plan_to_file(plan: str, request: str, output_dir: str = "plans", request_name: str = None):
    """
    Save the generated plan to a Markdown file for easy demo presentation.
    
    Files are saved with timestamp to avoid overwriting previous plans.
    Optionally includes request filename for easy matching.
    """
    import os
    from datetime import datetime
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate filename with timestamp and optional request name
    timestamp = datetime.now(TZ).strftime("%Y%m%d_%H%M%S")
    if request_name:
        # Extract base name from request file
        base_name = os.path.splitext(os.path.basename(request_name))[0]
        filename = f"{output_dir}/plan_{base_name}_{timestamp}.md"
    else:
        filename = f"{output_dir}/plan_{timestamp}.md"
    
    # Format content as Markdown
    content = f"""# Daily Plan
**Generated:** {datetime.now(TZ).strftime("%Y-%m-%d %H:%M:%S %Z")}

## Planning Request
{request}

---

## Generated Plan

{plan}

---

*Generated by AI Day Planner using OpenAI Function Calling*
"""
    
    # Write to file
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"✓ Plan saved to: {filename}")

# ========== Main Planning Loop ==========
def run(user_prompt: str, request_source: str = None):
    """
    Execute the planning loop with function calling.
    
    The LLM can call tools iteratively until it has enough information
    to produce a final plan.
    """
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    system = (
        "You are an intelligent day planner assistant using Europe/London timezone.\n\n"
        "Guidelines:\n"
        "- Always convert relative dates (like 'tomorrow') to explicit YYYY-MM-DD format\n"
        "- Check weather before recommending outdoor commute times\n"
        "- Always use find_free_slots before booking meetings\n"
        "- Consider travel times when suggesting meeting windows\n"
        "- If no free slots are found, suggest alternative time windows\n\n"
        "Output Format:\n"
        "After gathering all necessary information, produce a clear, well-formatted daily plan with:\n"
        "1. A brief summary paragraph\n"
        "2. A timeline of the day in bullet points with times, activities, and relevant details\n"
        "3. Any weather warnings or travel notes\n"
        "Make it easy to read and follow."
    )
    
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user_prompt}
    ]

    for iteration in range(8):  # Allow up to 8 tool calls
        resp = client.chat.completions.create(
            model=MODEL, 
            messages=messages, 
            tools=openai_tools_spec(), 
            tool_choice="auto", 
            temperature=0
        )
        
        m = resp.choices[0].message
        
        if m.tool_calls:
            # Model wants to call one or more tools
            messages.append({
                "role": "assistant",
                "content": m.content or "",
                "tool_calls": [tc.model_dump() for tc in m.tool_calls]
            })
            
            for tc in m.tool_calls:
                name = tc.function.name
                args = json.loads(tc.function.arguments or "{}")
                result = exec_tool(name, args)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "name": name,
                    "content": json.dumps(result, ensure_ascii=False)
                })
            continue
        else:
            # Model has produced final answer
            plan = m.content or ""
            print("\n" + "="*60)
            print("DAILY PLAN")
            print("="*60 + "\n")
            print(plan)
            print("\n" + "="*60 + "\n")
            
            # Save plan to file for easy demo presentation
            save_plan_to_file(plan, user_prompt, request_name=request_source)
            
            return plan
    
    print("\n[WARNING] Reached maximum iterations without final answer.")

def load_request_from_file(filepath: str) -> str:
    """Load planning request from a text file."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read().strip()
    
    # Replace "tomorrow" with actual date
    content = content.replace("tomorrow", tomorrow())
    
    return content

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="AI Day Planner - Plan your day with function calling",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use default example
  python planner.py
  
  # Use a specific request file
  python planner.py --request requests/example1_basic.txt
  
  # Custom inline request
  python planner.py --prompt "Plan my day: morning meeting at 9am, lunch at noon"
        """
    )
    
    parser.add_argument(
        "--request", "-r",
        type=str,
        help="Path to request file containing planning instructions"
    )
    
    parser.add_argument(
        "--prompt", "-p",
        type=str,
        help="Direct planning prompt (overrides --request)"
    )
    
    args = parser.parse_args()
    
    # Determine input source
    if args.prompt:
        # Direct prompt from command line
        prompt = args.prompt.replace("tomorrow", tomorrow())
        input_source = "command-line"
        request_file = None
    elif args.request:
        # Load from file
        prompt = load_request_from_file(args.request)
        input_source = args.request
        request_file = args.request
    else:
        # Default example
        prompt = (
            f"Please plan my day for {tomorrow()}:\n"
            f"- Morning: commute from Home to Office\n"
            f"- Afternoon: schedule a 30-minute 'FBA sync' meeting with Koust "
            f"between 14:00-16:00 and book it if you find a slot\n"
            f"- Check the weather and avoid rainy times for commuting if possible\n"
            f"- Estimate travel time (prefer walking or public transit)\n"
            f"- Present the final plan in a clear, readable format"
        )
        input_source = "default-example"
        request_file = None
    
    # Display context
    print("="*60)
    print("AI DAY PLANNER")
    print("="*60)
    print(f"Input source: {input_source}")
    print(f"Date: {tomorrow()}")
    print(f"Locations: Home (Glasgow) → Office")
    print(f"Attendees: {', '.join(ATTENDEES)}")
    print("="*60 + "\n")
    
    # Run planner with request source
    run(prompt, request_source=request_file)
