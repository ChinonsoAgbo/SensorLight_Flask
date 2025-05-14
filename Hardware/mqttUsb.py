import serial
import threading
import queue
import time
import paho.mqtt.client as mqtt

# Function to establish Serial connection with retry mechanism
def get_serial_connection():
    while True:
        try:
            ser = serial.Serial('/dev/ttyACM0', 2000000)
            #ser = serial.Serial('COM3', 2000000)
            print("Serial connected")
            return ser
        except serial.SerialException as e:
            print(f"Serial connection failed: {e}. Retrying in 3 seconds...")
            time.sleep(3)

# Function to establish MQTT connection with retry mechanism
def get_mqtt_connection():
    mqtt_client = mqtt.Client()
    mqtt_client.username_pw_set("SSD_Demo", "Bobbycar")
    while True:
        try:
            mqtt_client.connect("127.0.0.1", 1884, 60)
            print("MQTT connected")
            return mqtt_client
        except Exception as e:
            print(f"MQTT connection failed: {e}. Retrying in 3 seconds...")
            time.sleep(3)

# Thread-safe Queue
data_queue = queue.Queue()

# Setup Serial and MQTT connections
ser = get_serial_connection()
mqtt_client = get_mqtt_connection()

# Read data from Serial (Producer)
def serial_reader():
    while True:
        try:
            line = ser.readline().decode('utf-8').strip()
            data_queue.put(line)  # Push to queue
        except Exception as e:
            print(f"Serial Error: {e}. Retrying connection...")
            ser.close()
            ser = get_serial_connection()  # Reconnect if serial fails

# Send data to MQTT (Consumer)
def mqtt_sender():
    while True:
        data = data_queue.get()
        try:
            mqtt_client.publish("arduino/imuDaten", data)
            print(f"Sent: {data}")
        except Exception as e:
            print(f"MQTT Error: {e}. Retrying connection...")
            mqtt_client = get_mqtt_connection()  # Reconnect if MQTT fails
        data_queue.task_done()

# Start threads
threading.Thread(target=serial_reader, daemon=True).start()
threading.Thread(target=mqtt_sender, daemon=True).start()

# Keep main thread alive
while True:
    time.sleep(1)
