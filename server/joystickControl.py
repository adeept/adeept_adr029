#!/usr/bin/env python3
import RPi.GPIO as GPIO
import PCF8591 as ADC
#import Adafruit_PCA9685
import time

from adafruit_motor import servo
from adafruit_pca9685 import PCA9685
import busio
from board import SCL, SDA
i2c = busio.I2C(SCL, SDA)
pca = PCA9685(i2c, address=0x40) #default 0x40
pca.frequency = 50

L_btn = 17   # 11
R_btn = 18   #  12


def set_angle(ID, angle):
    servo_angle = servo.Servo(pca.channels[ID], min_pulse=500, max_pulse=2400,actuation_range=180)
    servo_angle.angle = angle

# pwm_init = 300        90°
# pwm_max  = 500        180°
# pwm_min  = 100        0°
 
angle = [90, 90, 90, 90, 90]    # The angle of all servos is 90°.
speed = 1 # servo rotation speed.
forward = 1
reverse = -1



mark = None
state_num = None
state_mark = None

def setup():
    ADC.setup(0X48)
    GPIO.setmode(GPIO.BCM)	# Numbers GPIOs by physical location
    GPIO.setup(L_btn, GPIO.IN, pull_up_down=GPIO.PUD_UP)	# Setup button pin as input an pull it up
    GPIO.setup(R_btn, GPIO.IN, pull_up_down=GPIO.PUD_UP)	# Setup button pin as input an pull it up
    

    set_angle(0, 90)
    set_angle(1, 90)
    set_angle(2, 90)
    set_angle(3, 90)
    set_angle(4, 90)



def ctrl_range(raw, max_genout, min_genout):
    if raw > max_genout:
        raw_output = max_genout
    elif raw < min_genout:
        raw_output = min_genout
    else:
        raw_output = raw
    return int(raw_output)

def rotation(ID, direction, speed):
    global angle
    if ID == None:
        pass
    else:
        if direction == 1:
            angle[ID] += speed
        else:
            angle[ID] -= speed
        if angle[ID] > 180:
            angle[ID] = 180
        if angle[ID] < 0:
            angle[ID] = 0
        set_angle(ID, angle[ID])

def move_servo(value):
    if value == 1:          # servo 1
        rotation(0, forward, speed) # (servo_ID, direction, speed)
    elif value == -1:
        rotation(0, reverse, speed)
    elif value == 2:        # servo 2
        rotation(1, forward, speed)
    elif value == -2:
        rotation(1, reverse, speed)
    elif value == 3:        # servo 3
        rotation(2, forward, speed)
    elif value == -3:
        rotation(2, reverse, speed)
    elif value == 4:        # servo 4
        rotation(4, forward, speed)
    elif value == -4:
        rotation(4, reverse, speed)
    else:
        rotation(None, reverse, speed)
    
def joystick(): #get joystick result.
    global state_num, state_mark
    #state_num 
    # 0 home
    # 1 L-pressed
    # 2 L-up
    # 3 L-down
    # 4 L-left 
    # 5 L-right
    # 6 R-home
    # 7 R-pressed
    # 8 R-up
    # 9 R down 
    # 10 R left 
    # 11 R right 
    # value number corresponds to servo number

    global state_num, state_mark
    state = ['home','L-pressed', 'L-up', 'L-down', 'L-left', 'L-right',\
             'R-home','R-pressed', 'R-up', 'R-down', 'R-left', 'R-right']

    value = None
    if GPIO.input(L_btn) == 0:
        value = 5
        state_num = 1 #L-pressed
    elif GPIO.input(R_btn) == 0:
        value = 6
        state_num = 7 #R-pressed
    else:
        value = 0
        state_num = 0

    if ADC.read(0) <= 30:  # servo 1 ############### fixed 
        value = 1 
        state_num = 3 # L-down
    elif ADC.read(0)>= 210 :   # servo 1
        value = -1
        state_num = 2 # L-right

    if ADC.read(1) >= 210:   # servo 2 ################ fixed
        value = 2
        state_num = 5 # L-right
    elif ADC.read(1) <= 30: 
        value = -2
        state_num = 4 # L-left

    if ADC.read(2) <= 30: # servo 3
        value = 3
        state_num = 9 # R-down 
    elif ADC.read(2)>= 210 :   # servo 3
        value = -3 
        state_num = 8 # R up 

    if ADC.read(3) <= 30:   # servo 4
        value = 4
        state_num = 10 # R-left 
    elif ADC.read(3) >= 210: 
        value = -4
        state_num = 11 # R-right 
    
    if state_mark != state_num: # print state
        print(state[state_num])
        state_mark = state_num
    return value

def loop():
    global mark
    value = joystick()
    move_servo(value)
    if mark != value:
        # print(value)
        mark = value
    time.sleep(0.01)

def destroy():
    GPIO.cleanup()   


if __name__ == '__main__':
    setup()
    # try:
    while True:
        loop()
    #except:
     #   destroy()

