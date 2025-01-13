import time
import ntptime
import json
import math
import constants
import urequests
import usocket as socket
from machine import ADC, Pin, I2C
from simple import MQTTClient
from connect_internet import connect
from mpu6500 import MPU6500

light_thresholds = {
    "midnight": 4000,
    "dawn": 6000,
    "morning": 9000,
    "noon": 11000,
    "afternoon": 8000,
    "evening": 6000,
}

def get_light_threshold():
    current_hour = (time.localtime()[3] + 2) % 24 # convert to UTC + 2
    if 0 <= current_hour < 5:
        return light_thresholds["midnight"]
    elif 5 <= current_hour < 8:
        return light_thresholds["dawn"]
    elif 8 <= current_hour < 12:
        return light_thresholds["morning"]
    elif 12 <= current_hour < 16:
        return light_thresholds["noon"]
    elif 16 <= current_hour < 19:
        return light_thresholds["afternoon"]
    else:
        return light_thresholds["evening"]

connect()
time.sleep(0.1)
ntptime.settime()

client = MQTTClient(constants.client_id, constants.mqtt_server)

i2c = I2C(0, scl=Pin(9), sda=Pin(8), freq=400000)
time.sleep(0.1)
mpu6500 = MPU6500(i2c)

photoresistor = ADC(Pin(28))
co2_sensor = ADC(Pin(26))

last_telegram_message = 0 # time in order to not spam with messages

bot_token = '8027770112:AAGo-2bpr0wFVhvoKbltoik0f2dErMg-VZo'
chat_id = '7864297252'

def send_telegram_message(message):
    global last_telegram_message
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}


    if time.time() - last_telegram_message > 60:
        last_telegram_message = int(time.time())
        try:
            response = urequests.post(url, json=payload)
            response.close()
            print("Message sent successfully!")
        except Exception as e:
            print(f"Error sending message: {e}")
        

# Initialize previous values for smoothing
prev_accel_x, prev_accel_y, prev_accel_z, prev_luminosity = 0, 0, 0, 0
def magnitude(x, y, z):
    return math.sqrt(x**2 + y**2 + z**2)

def compare_prev_accel(accel_x, accel_y, accel_z):
    if prev_accel_x == 0 or prev_accel_y == 0 or prev_accel_z == 0:
        return False
    return abs(accel_x - prev_accel_x) > 0.2 or abs(accel_y - prev_accel_y) > 0.2 or abs(accel_z - prev_accel_z) > 0.2

def detect_linear_movement(accel_x, accel_y, accel_z):
    global prev_accel_x, prev_accel_y, prev_accel_z
    # Calculate magnitude of acceleration
    accel_mag = magnitude(accel_x, accel_y, accel_z)
    if accel_mag > constants.LINEAR_ACCEL_THRESHOLD and compare_prev_accel(accel_x, accel_y, accel_z):
        prev_accel_x, prev_accel_y, prev_accel_z = accel_x, accel_y, accel_z
        return True

    prev_accel_x, prev_accel_y, prev_accel_z = accel_x, accel_y, accel_z
    return False

def detect_rotation(gyro_x, gyro_y, gyro_z):
    # Calculate magnitude of gyroscope values
    gyro_mag = magnitude(gyro_x, gyro_y, gyro_z)
    if gyro_mag > constants.GYRO_THRESHOLD:
        return True
    return False

def detect_fire(luminosity):
    if prev_luminosity == 0:
        return False
    print(f"Light threshold: {get_light_threshold()}")
    print(f"Previous Light threshold: {prev_luminosity}")
    print(f"Detect_fire result: {luminosity > get_light_threshold() and (luminosity - prev_luminosity > 400)}")

    return luminosity > get_light_threshold() and (luminosity - prev_luminosity > 400)

def write_register(addr, reg, data):
    i2c.writeto_mem(addr, reg, bytes([data]))

def read_register(addr, reg, nbytes=1):
    return i2c.readfrom_mem(addr, reg, nbytes)

def initialize_mpu_connection():
    device_id = read_register(constants.MPU_ADDR, constants.PICO_ADDR)[0]
    if device_id == 0x70:
        print("MPU Detected")
    else:
        print(f"Unexpected device ID: {device_id}")
        return False
    
    write_register(constants.MPU_ADDR, constants.PWR_MGMT_1, 0x00)
    print("MPU6500 initialized!")
    return True

def read_co2(samples=20):
    values = [co2_sensor.read_u16() for _ in range(samples)]
    return sum(values) / samples

def read_luminosity(samples=20):
    values = [photoresistor.read_u16() for _ in range(samples)]
    return sum(values) / samples
    
def send_post_request(addr, content):
    headers = {'Content-Type': 'application/json'}
    payload = {'message': content}
    response = urequests.post(addr, headers=headers, data=json.dumps(payload))
    response.close()

client.connect()
time.sleep(2)

try:
    if initialize_mpu_connection():
        while True:
            accel_x, accel_y, accel_z = mpu6500.acceleration
            gyro_x, gyro_y, gyro_z = mpu6500.gyro
            
            luminosity = read_luminosity()
            co2 = read_co2()
            
            linear_movement = detect_linear_movement(accel_x, accel_y, accel_z)
            fast_rotation = detect_rotation(gyro_x, gyro_y, gyro_z)

            # Prepare data to send to MQTT
            x = { "Warning": None, "Luminosity": luminosity, "CO2": co2, "X": accel_x,
                "Y": accel_y, "Z": accel_z, "GYRO_X": gyro_x, "GYRO_Y": gyro_y, "GYRO_Z": gyro_z}
            print(x)

            if linear_movement or fast_rotation:
                send_telegram_message("S-a produs o alunecare de teren!")
                x['Warning'] = 'Landslide'
                print("Fast movement detected!")
            
            # co2 threshold set in order to activate the fire 
            # warning because of the light (for presentation purposes)
            if  detect_fire(luminosity) and co2 > 20000:
                send_telegram_message("S-a produs un incendiu!")
                x['Warning'] = 'Fire'
                print('Fire detected')

            prev_luminosity = luminosity

            send_post_request("https://192.168.137.1:5000/info", x)
            client.publish(constants.topic, json.dumps(x))
            time.sleep(5)

except KeyboardInterrupt:
    print("Program stopped.")
