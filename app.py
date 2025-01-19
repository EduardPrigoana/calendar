import os
from flask import Flask, send_file, render_template_string
from icalendar import Calendar, Event
from datetime import datetime, timezone

app = Flask(__name__)

def trim_ics(input_file: str, output_file: str):
    """
    Trims events from the ICS file that occur before the current date and time.

    Parameters:
        input_file (str): Path to the input ICS file.
        output_file (str): Path to save the trimmed ICS file.
    """
    try:
        # Read the ICS file
        with open(input_file, 'r', encoding='utf-8') as file:
            calendar = Calendar.from_ical(file.read())

        # Get the current date and time in UTC
        now = datetime.now(timezone.utc)

        # Create a new calendar object for filtered events
        trimmed_calendar = Calendar()

        # Copy over all properties except events
        for key, value in calendar.items():
            trimmed_calendar.add(key, value)

        # Copy over events that are in the future
        for component in calendar.walk():
            if component.name == "VEVENT":
                start = component.get("DTSTART")

                # Handle both date and datetime
                if hasattr(start.dt, 'date'):
                    event_start = start.dt
                else:
                    event_start = datetime.combine(start.dt, datetime.min.time())

                # Ensure timezone-awareness when comparing
                if event_start.tzinfo is None:
                    event_start = event_start.replace(tzinfo=timezone.utc)

                if event_start >= now:
                    trimmed_calendar.add_component(component)

        # Write the trimmed calendar to the output file
        with open(output_file, 'wb') as file:
            file.write(trimmed_calendar.to_ical())

        print(f"Trimmed calendar saved to: {output_file}")

    except Exception as e:
        print(f"Error: {e}")

@app.route("/")
def index():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Calendar Trimmer</title>
    </head>
    <body>
        <h1>It works!</h1>
        <p><a href="/calendar-trimmed.ics">Download Trimmed Calendar</a></p>
    </body>
    </html>
    """
    return render_template_string(html_content)

@app.route("/calendar-trimmed.ics")
def serve_trimmed_calendar():
    input_file = os.path.abspath("calendar.ics")
    output_file = os.path.abspath("calendar-trimmed.ics")

    if not os.path.exists(input_file):
        return f"Error: Input file '{input_file}' not found.", 404

    try:
        trim_ics(input_file, output_file)

        if not os.path.exists(output_file):
            return "Error: Failed to create trimmed calendar file.", 500

        return send_file(output_file, as_attachment=True, mimetype="text/calendar")

    except FileNotFoundError as fnfe:
        return f"Error: {fnfe}", 404
    except Exception as e:
        return f"Error: {e}", 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
