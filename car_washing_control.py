import socket
import threading
import time
import RPi.GPIO as GPIO
import requests

post_once_done = False
post_once_done_2 = False
post_once_done_3 = False
in_work_flag = False
Car_ID = None
previous_speed_level = None


barrierStatus = 0
fanStatus = 0
waterTankStatus = 0

servoPIN = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(servoPIN, GPIO.OUT)
pwm = GPIO.PWM(servoPIN, 50)
pwm.start(0)
pwm.ChangeDutyCycle(75)

servo2PIN = 26
GPIO.setmode(GPIO.BCM)
GPIO.setup(servo2PIN, GPIO.OUT)
pwm2 = GPIO.PWM(servo2PIN, 50)
pwm2.start(0)
pwm2.ChangeDutyCycle(75)

TRIG = 23
ECHO = 24
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)


TRIG2 = 27
ECHO2 = 22
GPIO.setup(TRIG2, GPIO.OUT)
GPIO.setup(ECHO2, GPIO.IN)


TRIG3 = 21
ECHO3 = 19
GPIO.setup(TRIG3, GPIO.OUT)
GPIO.setup(ECHO3, GPIO.IN)

IN1 = 16
IN2 = 20
ENA_PIN = 12

GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)
GPIO.setup(ENA_PIN, GPIO.OUT)


GPIO.output(IN1, GPIO.HIGH)
GPIO.output(IN2, GPIO.LOW)

pwm1 = GPIO.PWM(ENA_PIN, 10)
pwm1.start(0)

def Json_Updater():
    global barrierStatus
    global fanStatus
    global waterTankStatus
    
    while True:
        if in_work_flag == False:
            if post_once_done:
                response = requests.get("https://carweb31.vercel.app/api/sensor/barrier")
                if response.status_code == 200:
                    data = response.json()
                    print("DATA:", data)
                        
                    entity = data.get('entity', {})
                    status = entity.get('status', None)
                    barrierStatus = entity.get('barrierStatus', None)
                    fanStatus = entity.get('fanStatus', None)
                    waterTankStatus = entity.get('waterTankStatus', None)

                    print("Status:", status)
                    print("Barrier Status:", barrierStatus)
                    print("Fan Status:", fanStatus)
                    print("Water Tank Status:", waterTankStatus)
                        
                else:
                    print("Hata kodu:", response.status_code)
        
        time.sleep(3)
        
def doorSpeed(speed_level):
    global in_work_flag
    global barrierStatus
    global previous_speed_level
    
    if speed_level == previous_speed_level:
        return
    
    try:
        if speed_level == "SLOW":
            print("inslow")
            sleep_duration = 0.02
        elif speed_level == "MID":
            print("inmid")
            sleep_duration = 0.01
        elif speed_level == "FAST":
            print("infast")
            sleep_duration = 0.005
        else:
            print("Gecersiz hiz seviyesi!")
            pwm.ChangeDutyCycle(2)
            return
        
        for i in range(90, 270, 5):
            aciAyarla(i)
            time.sleep(sleep_duration)
        
        previous_speed_level = speed_level
        
    except KeyboardInterrupt:
        GPIO.cleanup()
        pwm.stop()
        
def washTank(angle):
    try:
        if angle == "SLOW":
            aci2Ayarla(62)
        elif angle == "MID":
            aci2Ayarla(102)
        elif angle == "FAST":
            aci2Ayarla(182)
        else:
            print("Geçersiz açı!")
            aci2Ayarla(2)
            return
    
    except KeyboardInterrupt:
        GPIO.cleanup()
        pwm2.stop() 

def fanSpeed():
    global fanStatus
    try:
        if fanStatus == "SLOW":
            pwm1.ChangeDutyCycle(30)
        elif fanStatus == "MID":
            pwm1.ChangeDutyCycle(65)
        elif fanStatus == "FAST":
            pwm1.ChangeDutyCycle(100)
        else:
            pwm1.ChangeDutyCycle(0)
    except KeyboardInterrupt:
        GPIO.cleanup()
        pwm1.stop()
        
def closeDoor():
	for i in range(270,90,-1):
		aciAyarla(i)
		time.sleep(0.01)
	

def aciAyarla(aci):
    x = (1/180) * aci + 1
    duty = x * 5
    pwm.ChangeDutyCycle(duty)
    
def aci2Ayarla(aci):
    x = (1/180) * aci + 1
    duty = x * 5
    pwm2.ChangeDutyCycle(duty)
    
def distance():
    GPIO.output(TRIG, False)
    time.sleep(0.1)

    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    pulse_start = time.time()
    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()

    pulse_end = time.time()
    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150
    distance = round(distance, 2)
    return distance

def distance2():
    GPIO.output(TRIG2, False)
    time.sleep(0.1)

    GPIO.output(TRIG2, True)
    time.sleep(0.00001)
    GPIO.output(TRIG2, False)

    pulse_start2 = time.time()
    while GPIO.input(ECHO2) == 0:
        pulse_start2 = time.time()

    pulse_end2 = time.time()
    while GPIO.input(ECHO2) == 1:
        pulse_end2 = time.time()

    pulse_duration2 = pulse_end2 - pulse_start2
    distance2 = pulse_duration2 * 17150
    distance2 = round(distance2, 2)
    return distance2

def distance3():
    GPIO.output(TRIG3, False)
    time.sleep(0.1)

    GPIO.output(TRIG3, True)
    time.sleep(0.00001)
    GPIO.output(TRIG3, False)

    pulse_start3 = time.time()
    while GPIO.input(ECHO3) == 0:
        pulse_start3 = time.time()

    pulse_end3 = time.time()
    while GPIO.input(ECHO3) == 1:
        pulse_end3 = time.time()

    pulse_duration3 = pulse_end3 - pulse_start3
    distance3 = pulse_duration3 * 17150
    distance3 = round(distance3, 2)
    return distance3

def Car_arriwed():
    global Car_ID
    global post_once_done
    
    if not post_once_done:
            
        response = requests.post("https://carweb31.vercel.app/api/sensor/barrier")

        if response.status_code == 200:
            data = response.json()
            Car_ID = data['entity']['washedCar']['id']
            print("Car Arrived ID:", Car_ID)
            post_once_done = True
                
        else:
            print("Hata kodu:", response.status_code)
        
def Car_arriwed_wash():
    global Car_ID
    global post_once_done_2
    
    if not post_once_done_2:
        url = "https://carweb31.vercel.app/api/sensor/watertank"
        payload = {
            "id": Car_ID
        }
            
        response = requests.post(url, json=payload)

        if response.status_code == 200:
            data = response.json()
            print("Car Arrived ID:", data)
            post_once_done_2 = True
                
        else:
            print("Hata kodu:", response.status_code)
        time.sleep(1)

def Car_arriwed_fan():
    global Car_ID
    global post_once_done_3
    
    if not post_once_done_3:
        url = "https://carweb31.vercel.app/api/sensor/fan"
        payload = {
            "id": Car_ID
        }
            
        response = requests.post(url, json=payload)

        if response.status_code == 200:
            data = response.json()
            print("Car Arrived ID:", data)
            post_once_done_3 = True
                
        else:
            print("Hata kodu:", response.status_code)
        
        time.sleep(1)

def main_thread():
    global barrierStatus
    global fanStatus
    global waterTankStatus
    
    try:
        while True:
            dist = distance()
            dist2 = distance2()
            dist3 = distance3()
            
            print(dist)
            print(dist2)
            print(dist3)
            
            if dist < 10:
                print("Car_Arriwed")
                Car_arriwed()
                doorSpeed(barrierStatus)
            
            if dist2 < 10:
                print("Car_in_wash")
                Car_arriwed_wash()
                washTank(waterTankStatus)
                
                
            if dist3 < 10:
                print("Car_in_Fan")
                Car_arriwed_fan()
                fanSpeed()
                
            time.sleep(1)
                
    except KeyboardInterrupt:
        GPIO.cleanup()
        pwm.stop()
        pwm1.stop()
        
def fuction_thread():
    global barrierStatus
    global waterTankStatus
    global fanStatus
    
    try:
        while True:
            
            Json_Updater()
            
            if barrierStatus == "NONE":
                closeDoor()
                print("door_close")
            elif barrierStatus ==  "SLOW":
                doorSpeed(barrierStatus)
            elif barrierStatus == "MID":
                doorSpeed(barrierStatus)
            elif barrierStatus == "FAST":
                doorSpeed(barrierStatus)

            if waterTankStatus == "NONE":
                pwm2.ChangeDutyCycle(2)
            elif waterTankStatus == "SLOW":
                washTank(waterTankStatus)
            elif waterTankStatus == "MID":
                washTank(waterTankStatus)
            elif waterTankStatus == "FAST":
                washTank(waterTankStatus)
                
            if fanStatus == "NONE":
                pwm1.ChangeDutyCycle(0)
            elif fanStatus == "SLOW":
                pwm1.ChangeDutyCycle(35)
            elif fanStatus == "MID":
                pwm1.ChangeDutyCycle(65)
            elif fanStatus == "FAST":
                pwm1.ChangeDutyCycle(100)
                
        time.sleep(1)
            
    except KeyboardInterrupt:
        pass
    
if __name__ == "__main__":
    fuction_thread = threading.Thread(target=fuction_thread)
    main_thread = threading.Thread(target=main_thread)

    fuction_thread.start()
    main_thread.start()
    
    time.sleep(1)
