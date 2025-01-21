from flask import Flask, send_file
import os

app = Flask(__name__)

# Path to the provided calendar.ics file (default example)
ICS_FILE_PATH = 'calendar.ics'  # Path to your .ics file
TRIMMED_ICS_PATH = 'trimmed.ics'  # Path to save the trimmed .ics file

# Function to trim the .ics file
def trim_calendar_file():
    trimmed_content = []

    # Read the provided .ics file as a standard text file
    with open(ICS_FILE_PATH, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Keep the header lines up to X-WR-TIMEZONE
    for i, line in enumerate(lines):
        trimmed_content.append(line)
        if line.startswith("X-WR-TIMEZONE:Europe/Bucharest"):
            break

    # Find the first instance of "DTSTART:2025" and append subsequent lines
    include = False
    for line in lines:
        if not include and "DTSTART:2025" in line:
            include = True
        if include:
            trimmed_content.append(line)

    # Save the trimmed content to a new .ics file
    with open(TRIMMED_ICS_PATH, 'w', encoding='utf-8') as trimmed_f:
        trimmed_f.writelines(trimmed_content)

@app.route('/run')
def run_trim_command():
    # Delete the existing trimmed.ics file if it exists
    if os.path.exists(TRIMMED_ICS_PATH):
        os.remove(TRIMMED_ICS_PATH)

    # Regenerate the trimmed file
    trim_calendar_file()
    return "Trimmed .ics file has been regenerated successfully!"

@app.route('/trimmed.ics')
def download_trimmed_ics():
    if not os.path.exists(TRIMMED_ICS_PATH):
        return "The trimmed .ics file does not exist. Please run /run first.", 404
    return send_file(TRIMMED_ICS_PATH, as_attachment=True, mimetype='text/calendar')

@app.route('/')
def index():
    html_content = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>It works!</title>
    </head>
    <body>
        <h1>It works!</h1>
        <p>The trimmed calendar file can be generated and downloaded:</p>
        <a href="/run">Generate Trimmed ICS File</a><br>
        <a href="/trimmed.ics">Download Trimmed ICS File</a>
    </body>
    </html>
    '''
    return html_content

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)