# Sensor unit for monitoring conditions in a terrarium (software configuration) 🦎

This project is part of the practical section of my bachelor's thesis "Design and implementation of a sensor unit for monitoring environmental conditions in a terrarium". Submitted within the Applied Computer Science and Control program at the Faculty of Mechanical Engineering, Brno University of Technology (FME BUT).

## Overview
The goal was to create a compact hardware unit that measures temperature, humidity, light intensity and UV index. These parameters are crucial for ethical and successful reptile keeping. This software reads sensor data, processes it and transmits it to a cloud database for storage (InfluxDB) and visualisation (Grafana). These platforms are needed for full system functionality and their configuration is not cointained in this repository.

## Toolbox
**Hardware:** Raspberry Pico 2 W, SHT40, VEML7700, LTR390-UV
**Communication:** Wi-Fi, HiveMQ Cloud
**Database:** InfluxDB
**Firmware:** MicroPython

## Contents
`main.py` – firmware running on microcontroler that reads sensors via I2C, connects to Wi-Fi and publishes measurements to MQTT broker
`database.py` – bridge running on host PC that subscribes to MQTT topic and writes data to InfluxDB
`dashboard.html` – ...
`presentation.pdf` – ...

## Run project

1. Flash `main.py`to Raspberry Pi Pico 2W.
2. Run`main.py`and`database.py`in a terminal on host PC.
3. Open ...
---

**Name:** (future Bc.) Val (calex404)  
**Date:** April 2026

