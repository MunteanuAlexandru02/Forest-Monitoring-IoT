import paho.mqtt.client as mqtt
import matplotlib.pyplot as plt
from time import time

broker = '172.26.144.1'
port = 1883
topic = "senzori"
client_id = "python_subscriber"

def connect_mqtt():
    def on_connect(client, userdata, flags, rc, properties=None):
        if rc == 0:
            print(f"Connected to MQTT broker at {broker}:{port}")
            client.subscribe(topic)
            print(f"Subscribed to topic '{topic}'")
        else:
            print(f"Failed to connect, return code {rc}")

    client = mqtt.Client(client_id=client_id, protocol=mqtt.MQTTv5)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def on_message(client, userdata, msg):
    print(f"Message received on topic '{msg.topic}': {msg.payload.decode()}")


client = connect_mqtt()
client.on_message = on_message


try:
    client.loop_start()
    print("Listening for messages...")
    input("Press Enter to stop the client...\n")
finally:
    client.loop_stop()
    client.disconnect()
    print("MQTT client stopped.")
