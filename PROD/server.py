from flask import Flask

app = Flask(__name__)

@app.route('/hello')
def hello_funk():
    return "hello"

if __name__ == '__main__':
    app.run('localhost', 5000)
    
    