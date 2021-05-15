import RPi.GPIO as GPIO          
import os
import smtplib
import time
import sys, termios, tty
import Adafruit_DHT

from time import sleep
from picamera import PiCamera
from firebase import firebase
from pynput.keyboard import Key, Listener
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart


#Global Declarations

#for camera
camera = PiCamera()
tempValue=0

#for temp
sensor = Adafruit_DHT.DHT11
pin = 4

firebase = firebase.FirebaseApplication('https://security-33447-default-rtdb.asia-southeast1.firebasedatabase.app/', None)
firebase.put("/", "/temp", "0.00")
firebase.put("/", "/humidity", "0.00")

#for rovor
in1 = 23
in2 = 24
in3 = 17
in4 = 27
en = 25
temp1=1

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(in1,GPIO.OUT)
GPIO.setup(in2,GPIO.OUT)
GPIO.setup(in3,GPIO.OUT)
GPIO.setup(in4,GPIO.OUT)

GPIO.setup(en,GPIO.OUT)
GPIO.output(in1,GPIO.LOW)
GPIO.output(in2,GPIO.LOW)
GPIO.output(in3,GPIO.LOW)
GPIO.output(in4,GPIO.LOW)
p=GPIO.PWM(en,1000)
p.start(25)
print("\n")

#for ultrasonic
#GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM)
 
#set GPIO Pins
GPIO_TRIGGER = 5
GPIO_ECHO = 6

#set GPIO direction (IN / OUT)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)


 
def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
 
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def distance():
    # set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER, True)
 
    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)
 
    StartTime = time.time()
    StopTime = time.time()
 
    # save StartTime
    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time()
 
    # save time of arrival
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()
 
    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (TimeElapsed * 34300) / 2
 
    return distance


def SendMail(ImgFileName):
    img_data = open(ImgFileName, 'rb').read()
    msg = MIMEMultipart()
    msg['Subject'] = 'Captured Image'
    msg['From'] = 'Patrollingrobot24@gmail.com'
    msg['To'] = 'tejaswinimane.50@gmail.com'

    text = MIMEText("Image sent by rover")
    msg.attach(text)
    image = MIMEImage(img_data, name=os.path.basename(ImgFileName))
    msg.attach(image)

    s = smtplib.SMTP("smtp.gmail.com", 587)
    s.ehlo()
    s.starttls()
    s.ehlo()
    s.login("Patrollingrobot24@gmail.com", "security2407")
    s.sendmail("Patrollingrobot24@gmail.com", "tejaswinimane.50@gmail.com", msg.as_string())
    s.quit()
    print('Captured photo sent')


def Drive():
	global temp1
	os.system('clear')
        print('\n\n-----Rover Controls-----\nkeys   Funtion\nf       Forward\nb       Backward\ns       Stop\nq       Quit')
	while(1):


	    x=getch()

	    
	    if x=='s':
		print("stop")
		GPIO.output(in1,GPIO.LOW)
		GPIO.output(in2,GPIO.LOW)
		GPIO.output(in3,GPIO.LOW)
		GPIO.output(in4,GPIO.LOW)
		x='z'

	    elif x=='f':
		print("forward")
		GPIO.output(in1,GPIO.HIGH)
		GPIO.output(in2,GPIO.LOW)
		GPIO.output(in3,GPIO.HIGH)
		GPIO.output(in4,GPIO.LOW)
		temp1=1
		x='z'

	    elif x=='b':
		print("backward")
		GPIO.output(in1,GPIO.LOW)
		GPIO.output(in2,GPIO.HIGH)
		GPIO.output(in3,GPIO.LOW)
		GPIO.output(in4,GPIO.HIGH)
	        temp1=0
	        x='z'
	       
	    elif x=='q':
		print("Driving stoped")
		print('\n\n**********MENU**********\n1.Drive\n2.Capture Image\n3.Check Temperature\n4.Check Distance\n5.Check Humidity\n6.Exit\n7.Show Menu')
		break

	    else:
	        print("<<<  wrong data  >>>")
	        print("please enter the defined data to continue.....")



print('\n\n**********MENU**********\n1.Drive\n2.Capture Image\n3.Check Temperature\n4.Check Distance\n5.Check Humidity\n6.Exit\n7.Show Menu')
while True:

    print('\n\nEnter Your Command->')
    key=getch()
    
    #print('\nYou Entered {0}'.format( key))
    

    if key == '6':
        # Stop listener
        #return False
	print('close')
	break

    elif key == '1':
        print('Drive')
	Drive()
    
    elif key == '2':
        print('capturing image')
        camera.start_preview(alpha=192)
        sleep(2)
        tempValue+=1
        imgName='capturedImg'+str(tempValue)+'.jpg'
        camera.capture(imgName)
        camera.stop_preview()

        #Sending captured photo to Email
        print("sending file to Email ->" + imgName)
        SendMail(imgName)

    elif key == '3':
	print('Checking Temperature')
        humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
        if humidity is not None and temperature is not None:
                str_temp = ' {0:0.2f} *C '.format(temperature)
                str_hum  = ' {0:0.2f} %'.format(humidity)
                print('Temp={0:0.1f}*C '.format(temperature))
                firebase.put("/","/temp",str_temp)
                firebase.put("/","/humidity",str_hum)
        else:
                print('Failed to get reading. Try again!')

    elif key == '4':
	print('Calculating Distance')
	print('Ultrasonic')
	dist = distance()
	print ("Measured Distance = %.1f cm" % dist)




    elif key == '5':
	print('Checking Humidity')
        humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
        if humidity is not None and temperature is not None:
                str_temp = ' {0:0.2f} *C '.format(temperature)
                str_hum  = ' {0:0.2f} %'.format(humidity)
                print('Humidity=' + str_hum)
                firebase.put("/","/temp",str_temp)
                firebase.put("/","/humidity",str_hum)
        else:
                print('Failed to get reading. Try again!')

    elif key =='7':

	print('\n\n**********MENU**********\n1.Drive\n2.Capture Image\n3.Check Temperature\n4.Check Distance\n5.Check Humidity\n6.Exit\n7.Show Menu')

#final

camera.close()
GPIO.cleanup()

