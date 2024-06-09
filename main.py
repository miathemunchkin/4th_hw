import os
import json
import socket
import threading
from datetime import datetime
from flask import Flask, request, render_template, send_from_directory, abort

STATIC_FOLDER = "static"
TEMPLATE_FOLDER = "templates"
HTTP_PORT = 3000
SOCKET_PORT = 5000
DATA_FILE = "storage/data.json"

app = Flask(__name__, static_url_path='')

app.static_folder = STATIC_FOLDER
app.template_folder = TEMPLATE_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/message', methods=['GET', 'POST'])
def message():
    if request.method == 'POST':
        username = request.form['username']
        message = request.form['message']
        send_message_to_socket_server(username, message)
        return render_template('message.html', success=True)
    return render_template('message.html')

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory(STATIC_FOLDER, path)

@app.errorhandler(404)
def not_found(error):
    return render_template('error.html'), 404

def send_message_to_socket_server(username, message):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    data = json.dumps({
        "username": username,
        "message": message
    }).encode('utf-8')
    sock.sendto(data, ('localhost', SOCKET_PORT))
    sock.close()

def socket_server():
    if not os.path.exists(DATA_FILE):
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
        with open(DATA_FILE, 'w') as f:
            json.dump({}, f)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('localhost', SOCKET_PORT))

    while True:
        data, _ = sock.recvfrom(1024)
        message = json.loads(data.decode('utf-8'))
        timestamp = datetime.now().isoformat()
        with open(DATA_FILE, 'r+') as f:
            messages = json.load(f)
            messages[timestamp] = message
            f.seek(0)
            json.dump(messages, f, indent=4)

if __name__ == '__main__':
    threading.Thread(target=socket_server).start()
    app.run(port=HTTP_PORT, debug=True)