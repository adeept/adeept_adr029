import RPi.GPIO as GPIO
import PCF8591 as ADC
import time

btn = 12	# Define button pin

def setup():
    ADC.setup(0X48)
    GPIO.setmode(GPIO.BOARD)	# Numbers GPIOs by physical location
    GPIO.setup(btn, GPIO.IN, pull_up_down=GPIO.PUD_UP)	# Setup button pin as input an pull it up
    global state

def direction():    #get joystick result
    state = ['home', 'up', 'down', 'left', 'right', 'pressed']
    i = 0   

    if ADC.read(0) <= 5:
        i = 1        #up
    if ADC.read(0) >= 200: 
        i = 2        #down

    if ADC.read(1) <= 5: 
        i = 3        #left
    if ADC.read(1) >= 200:
        i = 4        #right

    # if GPIO.input(btn) == 0:
    #     i = 5        # Button pressed 

    # if GPIO.input(btn) == 1 and ADC.read(1) - 125 < 15 and ADC.read(1) - 125 > -15 and ADC.read(2) == 255:
    #     i = 0
    
    return state[i]

def loop(): 
    status = ''
    while True:
        tmp = direction()
        if tmp != None and tmp != status: 
            print(tmp)
            # z x y
            # print("z x y: ",GPIO.input(btn), ADC.read(1), ADC.read(2))
            status = tmp
        time.sleep(0.1)

def destroy():
    GPIO.cleanup()                     # Release resource

if __name__ == '__main__':        # Program start from here
    setup() 
    try:    
        loop()
    except KeyboardInterrupt:      # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
        destroy()




