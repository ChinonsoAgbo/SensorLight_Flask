import socket
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import threading
import time

app = Flask(__name__) # create web app instance
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*") # Enables web socket communication

TCP_HOST = '0.0.0.0' #  Listen on all available network interfaces
TCP_PORT = 5050 # Must match the Arduino's port
CONN_TIMEOUT = 10  # If no data is received in 10 seconds, consider the client disconnected ⚠️

exit_flag = False

''' Creat a TCP server TCP socket '''
def create_tcp_server():
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.bind((TCP_HOST, TCP_PORT))
    tcp_socket.listen(1) # only one connection at a time 
    tcp_socket.settimeout(1.0) # prevents blocking forever 
    print(f"✅ TCP Listening on {TCP_HOST}:{TCP_PORT}")
    return tcp_socket

tcp_socket = create_tcp_server() # ready to be connected
''' Server main loop '''
def tcp_data_receiver():
    global exit_flag
    conn = None
    last_heartbeat = time.time()

    while not exit_flag:
        try:
            if conn is None:
                print("🔄 Waiting for Arduino to connect...")
                conn, addr = tcp_socket.accept()
                conn.settimeout(1.0)  # Set timeout to detect lost connections
                print(f"✅ Arduino Connected: {addr}")
                last_heartbeat = time.time()

            while not exit_flag:
                try:
                    data = conn.recv(1024).decode().strip() # Receives data in a loop 

                    if not data:
                        raise ConnectionResetError("Connection lost.")

                    if data == "heartbeat":
                        last_heartbeat = time.time()
                        print("💓 Received heartbeat")
                    else:
                        print(f"📡 TCP Received: {data}")
                        try:
                            light_value = float(data)
                            socketio.emit('light_update', {'light': light_value})
                        except ValueError:
                            print("⚠️ Invalid data received")

                except socket.timeout:
                    if time.time() - last_heartbeat > CONN_TIMEOUT:
                        print("🚨 No heartbeat received. Closing connection...")
                        conn.close()
                        conn = None
                        break
                    continue

                except ConnectionResetError:
                    print("🚨 Arduino Disconnected! Waiting for reconnection...")
                    conn.close()
                    conn = None
                    break

        except Exception as e:
            print(f"🔥 TCP Accept Error: {e}")
            time.sleep(1)

tcp_thread = threading.Thread(target=tcp_data_receiver, daemon=True)
tcp_thread.start()

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
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
