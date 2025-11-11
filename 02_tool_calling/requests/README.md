# Planning Request Examples

This directory contains example planning requests that can be used as input for the day planner demo.

## How to Use

### Option 1: Use a specific request file

```bash
python planner.py --request requests/example1_basic.txt
```

### Option 2: Run all examples

```bash
python run_examples.py
```

This will process all request files in this directory and generate corresponding plan files.

## Creating Your Own Requests

Create a new `.txt` file in this directory with your planning request. The request should be in natural English and can include:

- **Time constraints**: "between 14:00-16:00", "in the morning"
- **Activities**: "meeting", "commute", "lunch"
- **Preferences**: "prefer walking", "avoid rain", "outdoor"
- **Attendees**: names or email addresses
- **Locations**: "Home", "Office", or custom locations

### Example Format

```
Plan my day for [date]:
- [Time]: [Activity] with [Person] ([duration])
- [Time range]: Find a slot for [Activity]
- Check [weather/travel/calendar]
- [Preferences and constraints]
```

## Example Files

- `example1_basic.txt` - Simple daily planning with meeting booking
- `example2_complex.txt` - Multiple meetings and complex scheduling
- `example3_weather_focused.txt` - Weather-dependent planning decisions

## Tips

- Be specific about times and durations
- Mention attendees explicitly for meeting bookings
- Include weather preferences for outdoor activities
- Specify travel modes (walk, bike, transit, drive)

