from flask import Flask

app = Flask(__name__)

@app.route('/hello')
def hello():
    return "hello world"

if __name__ == '__main__':
    app.run('localhost', 5000)
    
    