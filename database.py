import paho.mqtt.client as mqtt
import json
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from personal import *    


topic_subscription = "senzory"
bucket = "senzory"

influx = InfluxDBClient(url=influx_url, token=influx_token, org=influx_org)
write_api = influx.write_api(write_options=SYNCHRONOUS)

def zaznam(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        for sensor, hodnoty in data.items():
            point = Point("senzory") \
                .tag("senzor", sensor) \
                .field("teplota", hodnoty["teplota"]) \
                .field("vlhkost", hodnoty["vlhkost"])
            write_api.write(bucket=bucket, org=influx_org, record=point)
            print(f"Záznam o: {sensor}")
        print()
    except Exception as e:
        print("Error:", e)

client = mqtt.Client()
client.username_pw_set(mqtt_user, mqtt_password)
client.tls_set()
client.on_message = zaznam
client.connect(mqtt_host, 8883)
client.subscribe(topic_subscription)
print("Čakanie na dáta...")

client.loop_forever()