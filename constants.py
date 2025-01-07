MPU_ADDR = 0x68
PICO_ADDR = 0x75
PWR_MGMT_1 = 0x6B  # Power management register
ACCEL_XOUT_H = 0x3B  # Accelerometer output register

SSID = 'alexNet'
PASSWORD = 'alexMunteanu1'
mqtt_server = '192.168.137.1'
topic = 'senzori'
client_id = "pico_publisher"

LINEAR_ACCEL_THRESHOLD = int(2)
GYRO_THRESHOLD = int(3000)

LUMINOSITY_THRESHOLD = 65535

CO2_THRESHOLD = 15000

ALPHA = 0.1  # Smoothing factor for low-pass filter

GYRO_X = 0x43
GYRO_Y = 0x45
GYRO_Z = 0x47

FLASK_ADDR = "http://192.168.137.1:5000/app"