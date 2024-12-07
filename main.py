from machine import ADC, Pin, I2C
import time
import json
from network import WLAN, STA_IF
import usocket as socket
from simple import MQTTClient

SSID = 'AlexMHotspot'
PASSWORD = '57U13o;3'
mqtt_server = '192.168.137.1'
topic = 'senzori'
client_id = "pico_publisher"

wlan = WLAN(STA_IF)
wlan.active(True)
wlan.connect(SSID, PASSWORD)
while not wlan.isconnected():
    time.sleep(1)

MPU_ADDR = 0x68
PICO_ADDR = 0x75

PWR_MGMT_1 = 0x6B  # Power management register
ACCEL_XOUT_H = 0x3B  # Accelerometer output register

client = MQTTClient(client_id, mqtt_server)

i2c = I2C(0, scl=Pin(9), sda=Pin(8), freq=400000)
time.sleep(0.1)

photoresistor = ADC(Pin(27))
co2_sensor = ADC(Pin(26))

def write_register(addr, reg, data):
    i2c.writeto_mem(addr, reg, bytes([data]))

def read_register(addr, reg, nbytes=1):
    return i2c.readfrom_mem(addr, reg, nbytes)

def initialize_mpu_connection():
    device_id = read_register(MPU_ADDR, PICO_ADDR)[0]

    if device_id == 0x70:
        print("MPU Detected")
    else:
        print(f"Unexpected device ID: {device_id}")
        return False
    
    write_register(MPU_ADDR, PWR_MGMT_1, 0x00)
    print("MPU6500 initialized!")
    return True

def read_accelerometer():
    accel_data = i2c.readfrom_mem(MPU_ADDR, ACCEL_XOUT_H, 6)
    accel_x = int.from_bytes(accel_data[0:2], 'big', True)
    accel_y = int.from_bytes(accel_data[2:4], 'big', True)
    accel_z = int.from_bytes(accel_data[4:6], 'big', True)
    return accel_x, accel_y, accel_z

def read_co2():
    return co2_sensor.read_u16() # 65535 - normal

def read_luminosity():
    return photoresistor.read_u16() # 65535 - normal
client.connect()
time.sleep(2)
try:
    
    if initialize_mpu_connection():
        while True:
            accel_x, accel_y, accel_z = read_accelerometer()
            luminosity = read_luminosity()
            co2 = read_co2()
            x = {
                "Luminosity" : luminosity,
                "CO2" : co2,
                "X" : accel_x,
                "Y" : accel_y,
                "Z" : accel_z
            }
            print(x)
            client.publish(topic, json.dumps(x))
            time.sleep(1)
except KeyboardInterrupt:
    print("Program stopped.")
