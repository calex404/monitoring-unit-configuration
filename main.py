import machine
import utime
import network
from umqtt.simple import MQTTClient
import ssl
import json
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

topic_subscription = b"senzory"

def connect_mqtt():
    client = MQTTClient(
        client_id = "pico2w",
        server = mqtt_host,
        port = 8883,
        user = mqtt_user,
        password = mqtt_password,
        ssl = True,
        ssl_params = {"server_hostname": mqtt_host}
    )

    client.connect()
    print("MQTT pripojené.")
    print()
    return client

#   senzory

i2c = machine.I2C(0, scl=machine.Pin(1), sda=machine.Pin(0), freq=100000)

htu_address = 0x40
aht_address = 0x38
sht_address = 0x44

def read_htu():
    try:
        i2c.writeto(htu_address, b'\xFE')
        utime.sleep_ms(15)
        i2c.writeto(htu_address, b'\xF3')
        utime.sleep_ms(50)
        data_temp = i2c.readfrom(htu_address, 3)
        raw_temp = ((data_temp[0] << 8) | data_temp[1]) & 0xFFFC
        temperature = -46.85 + (175.72 * raw_temp / 65536)
        i2c.writeto(htu_address, b'\xF5')
        utime.sleep_ms(16)
        data_hum = i2c.readfrom(htu_address, 3)
        raw_hum = ((data_hum[0] << 8) | data_hum[1]) & 0xFFFC
        humidity = -6 + (125 * raw_hum / 65536)
        return temperature, humidity
    except:
        return None, None

def read_aht():
    try:
        i2c.writeto(aht_address, b'\xAC\x33\x00')
        utime.sleep_ms(80)
        data = i2c.readfrom(aht_address, 6)
        if (data[0] & 0x80):
            return None, None
        raw_hum = ((data[1] << 12) | (data[2] << 4) | (data[3] >> 4))
        humidity = (raw_hum / 1048576) * 100
        raw_temp = ((data[3] & 0x0F) << 16) | (data[4] << 8) | data[5]
        temperature = (raw_temp / 1048576) * 200 - 50
        return temperature, humidity
    except:
        return None, None

def read_sht():
    try:
        i2c.writeto(sht_address, b'\xFD')
        utime.sleep_ms(10)
        data = i2c.readfrom(sht_address, 6)
        raw_temp = (data[0] << 8) | data[1]
        temperature = -45 + (175 * raw_temp / 65535)
        raw_hum = (data[3] << 8) | data[4]
        humidity = -6 + (125 * raw_hum / 65535)
        return temperature, max(0, min(100, humidity))
    except:
        return None, None

connect_wifi()
client = connect_mqtt()

#   meranie

while True:
    t_htu, h_htu = read_htu()
    t_aht, h_aht = read_aht()
    t_sht, h_sht = read_sht()

    if t_htu is not None and t_aht is not None and t_sht is not None:
        print(f"HTU: {t_htu:>6.2f} °C | {h_htu:>6.2f} %")
        print(f"AHT:  {t_aht:>6.2f} °C | {h_aht:>6.2f} %")
        print(f"SHT:  {t_sht:>6.2f} °C | {h_sht:>6.2f} %")
        print()
    else:
        print("Chyba komunikacie.")

    if t_htu and t_aht and t_sht:
        measurements = json.dumps({
            "HTU": {"teplota": round(t_htu, 2), "vlhkost": round(h_htu, 2)},
            "AHT":  {"teplota": round(t_aht, 2), "vlhkost": round(h_aht, 2)},
            "SHT":  {"teplota": round(t_sht, 2), "vlhkost": round(h_sht, 2)}
        })
        client.publish(topic_subscription, measurements)

    utime.sleep(10)