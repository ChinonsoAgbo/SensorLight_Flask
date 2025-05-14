import serial
import threading
import queue
import time
import paho.mqtt.client as mqtt

# Setup Serial
#ser = serial.Serial('COM4', 230400)
ser = serial.Serial('/dev/ttyACM0', 2000000)
# Thread-safe Queue
data_queue = queue.Queue()

# Setup MQTT
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqtt_client.username_pw_set("SSD_Demo", "Bobbycar")
mqtt_client.connect("127.0.0.1", 1884, 60)

# Read data from Serial (Producer)
def serial_reader():
    while True:
        try:
            line = ser.readline().decode('utf-8').strip()
            data_queue.put(line)  # Push to queue
        except Exception as e:
            print("Serial Error:", e)

# Send data to MQTT (Consumer)
def mqtt_sender():
    while True:
        data = data_queue.get()
        try:
            mqtt_client.publish("arduino/imuDaten", data)
            print(f"{data}")
        except Exception as e:
            print("MQTT Error:", e)
        data_queue.task_done()

# Start threads
threading.Thread(target=serial_reader, daemon=True).start()
threading.Thread(target=mqtt_sender, daemon=True).start()

# Keep main thread alive
while True:
    time.sleep(1)
