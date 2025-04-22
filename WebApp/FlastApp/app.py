import json
import threading
import time
import csv
import paho.mqtt.client as mqtt
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

# MQTT configuration
# MQTT_BROKER = '172.20.10.14'  # Phone IP or hostname
MQTT_BROKER = '192.168.0.100'  # Router IP or hostname
MQTT_PORT = 1883              # Port number
MQTT_TOPIC = "arduino/imuDaten"  # Topic to subscribe to

exit_flag = False
data_buffer = []  # Stores data temporarily
buffer_lock = threading.Lock()

# MQTT Callbacks
def on_connect(client, userdata, flags, rc):
    print(f"✅ Connected to MQTT Broker with result code {rc}")
   # print(f"Subscribing to topic: {MQTT_TOPIC}")
    client.subscribe(MQTT_TOPIC, qos=2)  # Subscribe to the topic

def on_message(client, userdata, msg):
    #print(f"{msg.topic}: {msg.payload.decode()}")
    payload = msg.payload.decode("utf-8")
    try:
        json_data = json.loads(payload)
        #print(f" {json_data}")  
        if "imuData" in json_data:
            imu_data = {
                "acceleration": json_data["imuData"]["accelerationInGs"],
                "rotation": json_data["imuData"]["rotationInDegSec"],
                "timestampMillis": json_data["imuData"]["timestampMillis"]
            }
            #print(f"📡 MQTT Received: {imu_data}")

            # Send data to the frontend via WebSocket
            socketio.emit('imu_update', imu_data)

            # Add data to the buffer
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

 # MQTT setup
mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
def start_mqtt_client():
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
    mqtt_client.loop_start()  # Start the MQTT client loop to listen for incoming messages

# Start the MQTT client in a separate thread
mqtt_thread = threading.Thread(target=start_mqtt_client, daemon=True)
mqtt_thread.start()


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
    print("🌐 Starting Flask server...")
    print("🔗 Open http://localhost:5000 or http://127.0.0.1:5000 in your browser")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
