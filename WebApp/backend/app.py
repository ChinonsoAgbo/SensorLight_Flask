import json
import threading
import time
import csv
import paho.mqtt.client as mqtt
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from typing import List

# Initialize FastAPI
app = FastAPI()

# Mount templates and static folders (if needed)
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# MQTT configuration
MQTT_BROKER = '127.0.0.1'
#MQTT_BROKER = '192.168.0.100'
MQTT_PORT = 1884
MQTT_TOPIC = "arduino/imuDaten"

data_buffer = []
exit_flag = False
buffer_lock = threading.Lock()
last_save_time = time.time()
SAVE_INTERVAL = 60  # seconds

# Store active WebSocket connections
connected_clients: List[WebSocket] = []

# MQTT Callbacks
def on_connect(client, userdata, flags, reason_code, properties):
    print(f"✅ Connected to MQTT Broker with result code {reason_code}")
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    global last_save_time, data_buffer
    payload = msg.payload.decode("utf-8")
    try:
        parts = payload.strip().split(",")
        acc_x = float(parts[0])
        acc_y = float(parts[1])
        acc_z = float(parts[2])
        gyro_z = float(parts[3])
        timestamp = int(parts[4])
        imu_data = {
            "acceleration": {"x": acc_x, "y": acc_y, "z": acc_z},
            "rotation": {"z": gyro_z},
            "timestampMillis": timestamp
        }

        print(f"{imu_data}")

        # Send to all connected WebSocket clients
        for ws in connected_clients:
            try:
                ws.send_text(json.dumps(imu_data))
            except:
                continue

        # Buffer data
        with buffer_lock:
            data_buffer.append([acc_x, acc_y, acc_z, gyro_z, timestamp])
            now = time.time()
            if now - last_save_time >= SAVE_INTERVAL:
                filename = time.strftime("sensor_data_%Y-%m-%d_%H-%M-%S.csv")
                with open(filename, 'w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(["Acc_X", "Acc_Y", "Acc_Z", "Rot_Z", "Millis"])
                    writer.writerows(data_buffer)
                print(f"💾 Data saved to {filename}")
                data_buffer = []
                last_save_time = now

    except Exception as e:
        print(f"❌ Failed to parse IMU data: {payload}")
        print(f"⚠️ Error: {e}")

# MQTT setup
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqtt_client.username_pw_set("SSD_Demo", "Bobbycar")
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

def start_mqtt_client():
    while True:
        try:
            print("🔄 Attempting to connect to MQTT Broker...")
            mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
            mqtt_client.loop_start()
            break # Exit loop on successful connection
        except Exception as e:
            print(f"❌ Failed to connect to MQTT Broker: {e}")
            print(f"🔄 Retrying in 2 seconds...")
            time.sleep(2)


# Start MQTT in a thread
mqtt_thread = threading.Thread(target=start_mqtt_client, daemon=True)
mqtt_thread.start()

# Route to render frontend
@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    print("✅ WebSocket client connected")
    try:
        while True:
            await websocket.receive_text()  # optionally handle input
    except WebSocketDisconnect:
        connected_clients.remove(websocket)
        print("❌ WebSocket client disconnected")
