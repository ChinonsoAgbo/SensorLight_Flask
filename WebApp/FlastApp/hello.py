import socket
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

# TCP Socket Setup
tcp_host = '0.0.0.0'  # Listen on all interfaces
tcp_port = 5000

tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_socket.bind((tcp_host, tcp_port))
tcp_socket.listen(1)

print(f"TCP Listening on {tcp_host}:{tcp_port}")

def tcp_data_receiver():
    while True:
        try:
            conn, addr = tcp_socket.accept()
            print(f"TCP Connected by {addr}")
            data = conn.recv(1024).decode().strip()
            if data:
                print(f"TCP Received: {data}")
                try:
                    light_value = float(data)
                    socketio.emit('light_update', {'light': light_value})

                except ValueError:
                    print("Received non-numeric data from TCP")
            conn.close()
        except Exception as e:
            print(f"TCP Error: {e}")

import threading
threading.Thread(target=tcp_data_receiver).start()

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def connect():
    print('Client connected to WebSocket')

@socketio.on('disconnect')
def disconnect():
    print('Client disconnected from WebSocket')

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5050, debug=True) #change the port to 5000, to avoid conflicts with TCP port.