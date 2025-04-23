import paho.mqtt.client as mqtt
topic ="arduino/imuDaten"  # Replace with your topic

def on_connect(client, userdata, flags, rc):
    print(f"✅ Connected to MQTT Broker with result code {rc}")
    client.subscribe(topic, qos=2)  # Subscribe to the topi

def on_message(client, userdata, msg):
    print(f"Received: {msg.payload.decode()} on topic {msg.topic}")

client = mqtt.Client()
client.username_pw_set("chinonso", "yourpassword")
client.on_connect = on_connect
client.on_message = on_message

client.connect("172.20.10.14", 1883, 60)  # Replace with broker IP if not local
client.loop_forever()