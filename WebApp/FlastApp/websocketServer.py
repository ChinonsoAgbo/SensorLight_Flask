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
    tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    tcp_socket.bind((TCP_HOST, TCP_PORT))
    tcp_socket.listen(1)
    print(f"✅ TCP Listening on {TCP_HOST}:{TCP_PORT}")
    return tcp_socket

tcp_socket = create_tcp_server()

def tcp_data_receiver():
    global exit_flag
    conn = None
    recv_buffer = ""

    while not exit_flag:
        try:
            if conn is None:
                print("🔄 Waiting for Arduino to connect...")
                conn, addr = tcp_socket.accept()
                conn.settimeout(None)
                print(f"✅ Arduino Connected: {addr}")

            while not exit_flag:
                chunk = conn.recv(1024).decode('utf-8')
                if not chunk:
                    print("⚠️ Connection closed by client")
                    conn.close()
                    conn = None
                    break

                recv_buffer += chunk
                while '\n' in recv_buffer:
                    line, recv_buffer = recv_buffer.split('\n', 1)
                    line = line.strip()
                    if line:
                        print(f"📡 TCP Received: {line}")
                        try:
                            json_data = json.loads(line)

                            if "imuData" in json_data:
                                imu_data = {
                                    "acceleration": json_data["imuData"]["accelerationInGs"],
                                    "rotation": json_data["imuData"]["rotationInDegSec"],
                                    "timestampMillis": json_data["imuData"]["timestampMillis"]
                                }

                                socketio.emit('imu_update', imu_data)  # send to frontend

                                with buffer_lock:
                                    data_buffer.append([
                                        json_data["imuData"]["accelerationInGs"]["x"],
                                        json_data["imuData"]["accelerationInGs"]["y"],
                                        json_data["imuData"]["accelerationInGs"]["z"],
                                        # json_data["imuData"]["rotationInDegSec"]["x"],
                                        # json_data["imuData"]["rotationInDegSec"]["y"],
                                        json_data["imuData"]["rotationInDegSec"]["z"],
                                        json_data["imuData"]["timestampMillis"]
                                    ])
                            else:
                                print("⚠️ Incomplete JSON data received")
                        except json.JSONDecodeError:
                            print("❌ Invalid JSON data received")

        except ConnectionResetError:
            print("🚨 Connection Reset! Waiting for Arduino to reconnect...")
            if conn:
                conn.close()
            conn = None
        except Exception as e:
            print(f"🔥 TCP Error: {e}")
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
                    writer.writerow(["Acc_X", "Acc_Y", "Acc_Z", "Rot_Z", "Millis"])  # CSV header
                    writer.writerows(data_buffer)
                print(f"💾 Data saved to {filename}")
                data_buffer = []

csv_thread = threading.Thread(target=save_data_to_csv, daemon=True)
csv_thread.start()

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def connect():
    print('✅ Client connected to WebSocket')

@socketio.on('disconnect')
def disconnect():
    print('❌ Client disconnected from WebSocket')

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
