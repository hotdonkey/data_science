from flask import Flask, request

app = Flask(__name__)

@app.route('/hello')
def hello_funk():
    return "hello"

@app.route('/')
def index():
    return "Test message. The server is running"

if __name__ == '__main__':
    app.run('localhost', 8000)
    
    