import machine
import utime
import network
import ssl
import json
from umqtt.simple import MQTTClient
from personal import *    


def connect_wifi():
    connection = network.WLAN(network.STA_IF)
    connection.active(True)
    connection.connect(ssid, wifi_password)
    print("Pripájanie...")
    print()
    for _ in range(60):
        if connection.isconnected():
            print("WiFi pripojená.")
            print()
            return True
        utime.sleep(1)
    print("Pripojenie zlyhalo!")
    return False

topic = b"senzory"

def connect_mqtt():
    broker = MQTTClient(
        client_id = "pico2w",
        server = mqtt_host,
        port = 8883,
        user = mqtt_user,
        password = mqtt_password,
        ssl = True,
        ssl_params = {"server_hostname": mqtt_host}
    )
    broker.connect()
    print("MQTT pripojené.")
    print()
    return broker

i2c = machine.I2C(0, scl=machine.Pin(1), sda=machine.Pin(0), freq=100000) # pinout

sht_address = 0x44
veml_address = 0x10
ltr_address = 0x53

# temperature and humidity sensor SHT40
def read_sht40():
    try:
        i2c.writeto(sht_address, bytes([0xFD]))
        utime.sleep_ms(10)
        data = i2c.readfrom(sht_address, 6)
        raw_data_temperature = (data[0] << 8) | data[1]
        temperature = float(-45 + 175 * raw_data_temperature / 65535)
        raw_data_humidity = (data[3] << 8) | data[4]
        humidity = float(-6 + 125 * raw_data_humidity / 65535)
        return round(temperature, 2), round(humidity, 2)
    except:
        return None, None

# light intensity sensor VEML7700
def read_veml7700():
    try:
        i2c.writeto_mem(veml_address, 0x00, bytes([0x00, 0x00]))
        utime.sleep_ms(200)
        data = i2c.readfrom_mem(veml_address, 0x04, 2)
        raw_data = data[0] | (data[1] << 8)
        light_intensity = float(raw_data * 0.0576)
        return round(light_intensity, 2)
    except:
        return None

# uv sensor LTR390-UV
def read_ltr390():
    try:
        i2c.writeto(ltr_address, bytes([0x00, 0x0A]))
        utime.sleep_ms(200)
        i2c.writeto(ltr_address, bytes([0x10]))
        data = i2c.readfrom(ltr_address, 3)
        raw_data = data[0] | (data[1] << 8) | (data[2] << 16)
        uv_index = float(raw_data / 2300)
        return round(uv_index, 2)
    except:
        return None

connect_wifi()
broker = connect_mqtt()

while True:
    temperature, humidity = read_sht40()
    light_intensity = read_veml7700()
    uv_index = read_ltr390()

    print(f"SHT40:   {temperature} °C | {humidity} %")
    print(f"VEML7700: {light_intensity} lux")
    print(f"LTR390:   {uv_index} UV index")
    print()

    if temperature is not None and humidity is not None and light_intensity is not None and uv_index is not None:
        measurements = json.dumps({
            "SHT40":   {"teplota": temperature, "vlhkost": humidity},
            "VEML7700": {"intenzita_svetla": light_intensity},
            "LTR390":   {"uv_index": uv_index}
        })
        broker.publish(topic, measurements)
    utime.sleep(10)