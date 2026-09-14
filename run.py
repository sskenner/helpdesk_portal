import webbrowser, logging
from threading import Timer
from waitress import serve

from app import app

logging.basicConfig(level=logging.INFO)

def open_browser():
    webbrowser.open_new('http://127.0.0.1:8080/launch')

if __name__ == '__main__':
    Timer(1, open_browser).start()
    # app.run(debug=True, port=8080, host='0.0.0.0')
    serve(app, host='127.0.0.1', port=8080)