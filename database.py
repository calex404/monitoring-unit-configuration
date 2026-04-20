import paho.mqtt.client as mqtt
import json
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from personal import *    


topic = "senzory"
bucket = "senzory"

# InfluxDB connection
influx = InfluxDBClient(url=influx_url, token=influx_token, org=influx_org)
api = influx.write_api(write_options=SYNCHRONOUS)

def zaznam(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        for sensor, measurement in data.items():
            point = Point("senzory") \
                .tag("senzor", sensor)
            for key, value in measurement.items():
                point = point.field(key, value)
            api.write(bucket=bucket, org=influx_org, record=point)
            print(f"Záznam o: {sensor} uložený.")
        print()
    except Exception as e:
        print("Error:", e)

# MQTT connection
broker = mqtt.Client()
broker.username_pw_set(mqtt_user, mqtt_password)
broker.tls_set()                                   # TLS encryption
broker.on_message = zaznam
broker.connect(mqtt_host, 8883)
broker.subscribe(topic)

print("Čakanie na dáta...")
broker.loop_forever()