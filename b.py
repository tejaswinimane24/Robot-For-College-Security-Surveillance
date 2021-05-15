import RPi.GPIO as GPIO
from time import sleep
from firebase import firebase
import Adafruit_DHT

sensor = Adafruit_DHT.DHT11
pin = 4

firebase = firebase.FirebaseApplication('https://security-33447-default-rtdb.asia-southeast1.firebasedatabase.app/', None)
firebase.put("/", "/temp", "0.00")
firebase.put("/", "/humidity", "0.00")

while True:
        humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
        if humidity is not None and temperature is not None:
        	str_temp = ' {0:0.2f} *C '.format(temperature)
        	str_hum  = ' {0:0.2f} %'.format(humidity)
        	print('Temp={0:0.1f}*C  Humidity={1:0.1f}%'.format(temperature,humidity))
        	firebase.put("/","/temp",str_temp)
        	firebase.put("/","/humidity",str_hum)
        else:
        	print('Failed to get reading. Try again!')
        sleep(5)