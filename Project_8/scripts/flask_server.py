from flask import Flask, request
import subprocess

app = Flask(__name__)

@app.route('/')
def index():
    return "The server is running"

@app.route('/parser', methods=['POST'])
def parser_route():
    try:
        # Execute the parser script as a subprocess
        process = subprocess.run(
            ['python', 'parser.py'], capture_output=True, text=True)
        # Get the output from the subprocess
        output = process.stdout
        return output
    except Exception as e:
        return str(e)

@app.route('/db_push', methods=['POST'])
def db_push_route():
    try:
        # Execute the db_push script as a subprocess
        process = subprocess.run(
            ['python', 'db_push.py'], capture_output=True, text=True)
        # Get the output from the subprocess
        output = process.stdout
        return output
    except Exception as e:
        return str(e)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)