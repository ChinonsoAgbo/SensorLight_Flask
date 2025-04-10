import socket
import json
import threading
import time
import csv
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)  
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

TCP_HOST = '0.0.0.0'
TCP_PORT = 5050
CONN_TIMEOUT = 10  

exit_flag = False
data_buffer = []  # Stores data temporarily
buffer_lock = threading.Lock()

def create_tcp_server():
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.bind((TCP_HOST, TCP_PORT))
    tcp_socket.listen(1)
    tcp_socket.settimeout(None)  
    print(f"✅ TCP Listening on {TCP_HOST}:{TCP_PORT}")
    return tcp_socket

tcp_socket = create_tcp_server()

def tcp_data_receiver():
    global exit_flag
    conn = None
    last_heartbeat = time.time()

    while not exit_flag:
        try:
            if conn is None:
                print("🔄 Waiting for Arduino to connect...")
                conn, addr = tcp_socket.accept()
                conn.settimeout(None)  
                print(f"✅ Arduino Connected: {addr}")
                last_heartbeat = time.time()

            while not exit_flag:
                try:
                    data = conn.recv(1024).decode().strip()

                    # if not data:
                    #     print("⚠️ Empty data received. Waiting for more...")
                    #     continue

                    # if data == "heartbeat":
                    #     last_heartbeat = time.time()
                    #     print("💓 Received heartbeat")
                    # else:
                    print(f"📡 TCP Received: {data}")

                    try:
                        json_data = json.loads(data)
                        timestamp = time.strftime("%H:%M:%S", time.localtime())

                        if all(k in json_data for k in ["x", "y", "z"]):
                            imu_data = {
                                "timestamp": timestamp,
                                "type": "IMU",
                                "x": json_data["x"],
                                "y": json_data["y"],
                                "z": json_data["z"]
                            }
                            socketio.emit('imu_update', imu_data)

                            # Save to buffer
                            with buffer_lock:
                                data_buffer.append([timestamp, json_data["x"], json_data["y"], json_data["z"]])

                    except json.JSONDecodeError:
                        print("⚠️ Invalid JSON data received")

                except socket.timeout:
                    if time.time() - last_heartbeat > CONN_TIMEOUT:
                        print("⚠️ No heartbeat received, but keeping connection open...")
                        last_heartbeat = time.time()  
                        continue  
                    continue

                except ConnectionResetError:
                    print("🚨 Connection Reset! Waiting for Arduino to reconnect...")
                    conn.close()
                    conn = None
                    break

        except Exception as e:
            print(f"🔥 TCP Accept Error: {e}")
            time.sleep(1)

tcp_thread = threading.Thread(target=tcp_data_receiver, daemon=True)
tcp_thread.start()

def save_data_to_csv():
    global data_buffer
    while not exit_flag:
        time.sleep(180)  # Wait 3 minutes
        with buffer_lock:
            if data_buffer:
                filename = time.strftime("sensor_data_%Y-%m-%d_%H-%M-%S.csv")
                with open(filename, 'w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(["Time", "X", "Y", "Z"])  # CSV header
                    writer.writerows(data_buffer)  # Write buffered data
                print(f"💾 Data saved to {filename}")
                data_buffer = []  # Clear buffer after saving

csv_thread = threading.Thread(target=save_data_to_csv, daemon=True)
csv_thread.start()

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
