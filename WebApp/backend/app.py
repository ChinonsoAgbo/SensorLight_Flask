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
MQTT_PORT = 1884              # Port number
MQTT_TOPIC = "arduino/imuDaten"  # Topic to subscribe to
data_buffer = []
exit_flag = False
buffer_lock = threading.Lock()
last_save_time = time.time()  # initialize
SAVE_INTERVAL = 60  # seconds (3 minutes)

# MQTT Callbacks
def on_connect(client, userdata, flags, reason_code, properties):
    print(f"✅ Connected to MQTT Broker with result code {reason_code}")
   # print(f"Subscribing to topic: {MQTT_TOPIC}")
    client.subscribe(MQTT_TOPIC)  # Subscribe to the topic

def on_message(client, userdata, msg):
    global last_save_time, data_buffer
    #print(f"{msg.topic}: {msg.payload.decode()}")
    payload = msg.payload.decode("utf-8")
    try:
        #print(f" {json_data}")  
        # Example payload: "t:123456; acc:0.12,0.34,0.56; gyro:-0.78"
        parts = payload.strip().split(",")
        acc_x = float(parts[0])
        acc_y = float(parts[1])
        acc_z = float(parts[2])
        gyro_z = float(parts[3])
        timestamp = int(parts[4])
        imu_data = { 
            "acceleration": {
                "x": acc_x,
                "y": acc_y,
                "z": acc_z
            },
            "rotation": {
                "z": gyro_z
            },
            "timestampMillis": int(timestamp)
        }

        print(f"{imu_data}"    )
        # Send data to the frontend via WebSocket
        socketio.emit('imu_update', imu_data) # send to frontend web socket 

        # Add data to the buffer
        with buffer_lock:
            data_buffer.append([acc_x, acc_y, acc_z, gyro_z, timestamp])

             # ✅ Check if it's time to save
            now = time.time()
            if now - last_save_time >= SAVE_INTERVAL:
                filename = time.strftime("sensor_data_%Y-%m-%d_%H-%M-%S.csv")
                with open(filename, 'w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(["Acc_X", "Acc_Y", "Acc_Z", "Rot_Z", "Millis"])
                    writer.writerows(data_buffer)
                print(f"💾 Data saved to {filename}")
                data_buffer = []  # clear buffer
                last_save_time = now  # reset timer

    except Exception as e:
        print(f"❌ Failed to parse IMU data: {payload}")
        print(f"⚠️ Error: {e}")

 # MQTT setup
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqtt_client.username_pw_set("SSD_Demo","Bobbycar")
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
def start_mqtt_client():
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
    mqtt_client.loop_start()  # Start the MQTT client loop to listen for incoming messages

# Start the MQTT client in a separate thread
mqtt_thread = threading.Thread(target=start_mqtt_client, daemon=True)
mqtt_thread.start()


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
