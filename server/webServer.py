#!/usr/bin/python3
# File name   : setup.py
# Author      : Adeept Devin
# Date        : 2022/7/12
import time
import threading
import RPIservo
import os
import socket
import info

import RPi.GPIO as GPIO
import PCF8591 as ADC

# websocket
import asyncio
import websockets

import json
import app


state_num = None
state_mark = None
servoD_mark = None
joystick_mark = 1
joystick_button_mark = 0

# 舵机转动到初始位置
# The servo turns to the initial position.
scGear = RPIservo.ServoCtrl()
scGear.moveInit()
scGear.start()

'''
joystick_sc = RPIservo.ServoCtrl()
joystick_sc.moveInit()
'''
# 获取舵机初始角度
# Get the initial angle of the servo.
init_servo0 = scGear.initAngle[0]
init_servo1 = scGear.initAngle[1]
init_servo2 = scGear.initAngle[2]
init_servo3 = scGear.initAngle[3]
init_servo4 = scGear.initAngle[4]

curpath = os.path.realpath(__file__)
thisPath = "/" + os.path.dirname(curpath)

direction_command = 'no'
turn_command = 'no'

def servoAngleInit():
    # A_sc.initConfig(1, init_servo0, 1)
    # B_sc.initConfig(1, init_servo1, 1)
    # C_sc.initConfig(1, init_servo2, 1)
    # D_sc.initConfig(1, init_servo3, 1)
    # E_sc.initConfig(1, init_servo4, 1)
    pass

# 修改舵机中位
# Modify the initial position of the servo.
def replace_num(initial,new_num):   #Call this function to replace data in '.txt' file
    global r
    newline=""
    str_num=str(new_num)
    with open(thisPath+"/RPIservo.py","r") as f:
        for line in f.readlines():
            if(line.find(initial) == 0):
                line = initial+"%s" %(str_num+"\n")
            newline += line
    with open(thisPath+"/RPIservo.py","w") as f:
        f.writelines(newline)

# 树莓派开启WiFi热点。
# Raspberry Pi turns on WiFi hotspot.
def ap_thread():
    os.system("sudo create_ap wlan0 eth0 Adeept_Robot 12345678")

# WEB界面控制舵机
# WEB interface to control the servo.
def robotCtrl(command_input, response):
    global direction_command, turn_command
    #print(command_input)
    if command_input == "A_add":
        scGear.singleServo(0, 1, 1) # (servoPort, direction, speed)

    elif command_input == "A_minus":
        scGear.singleServo(0, -1, 1)

    elif command_input == "AS":
        scGear.stopWiggle()

    elif command_input == "B_add":
        scGear.singleServo(1, -1, 1) # (servoPort, direction, speed)

    elif command_input == "B_minus":
        scGear.singleServo(1, 1, 1)

    elif command_input == "BS":
        scGear.stopWiggle()
        
    elif command_input == "C_add":
        scGear.singleServo(2, 1, 1) # (servoPort, direction, speed)
    elif command_input == "C_minus":
        scGear.singleServo(2, -1, 1)
    elif command_input == "CS":
        scGear.stopWiggle()
        
    elif command_input == "D_add":
        scGear.singleServo(3, 1, 1) # (servoPort, direction, speed)
    elif command_input == "D_minus":
        scGear.singleServo(3, -1, 1)
    elif command_input == "DS":
        scGear.stopWiggle()
        
    elif command_input == "E_add":
        scGear.singleServo(4, 1, 1) # (servoPort, direction, speed)
    elif command_input == "E_minus":
        scGear.singleServo(4, -1, 1)
    elif command_input == "ES":
        scGear.stopWiggle()

    elif command_input == 'save_pos':
        Pos = scGear.servoAngle()
        newPos = []
        for i in range(0, 5):
            newPos.append(Pos[i])
        print("save_pos:",newPos)
        scGear.newPlanAppend(newPos)
    
    elif command_input == 'stop':
        scGear.moveThreadingStop()

    elif command_input == 'cerate_Plan':
        scGear.createNewPlan()

    elif command_input == 'plan':
        scGear.planThreadingStart()
        scGear.angleUpdate()

    elif command_input == 'save_Plan':
        scGear.savePlanJson()
        pass

def configInitAngle(command_input, response):
    pass

# 摇杆初始化
# Joystick initialization.
def joystickSetup():
    ADC.setup(0X48)
    GPIO.setmode(GPIO.BCM)	# Numbers GPIOs by physical location
    GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)	# Setup Left button pin as input an pull it up
    GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)	# Setup Right button pin as input an pull it up

# 读取摇杆值
# read joystick value.
def joystick():
    global state_num, state_mark, servoD_mark
    L_btn = 17
    R_btn = 18
    state = ['home','L-pressed', 'L-up', 'L-down', 'L-left', 'L-right',\
             'R-home','R-pressed', 'R-up', 'R-down', 'R-left', 'R-right']
    value = None
    if GPIO.input(L_btn) == 0:
        value = 5
        state_num = 1
        servoD_mark = 1
    elif GPIO.input(R_btn) == 0:
        value = 6
        state_num = 7
        servoD_mark = 0
    else:
        value = 0
        state_num = 0
    if ADC.read(0) <= 30:  # servo A
        value = 1 
        state_num = 3
    elif ADC.read(0)>= 210 :   # servo A
        value = -1
        state_num = 2

    if ADC.read(1) >= 210:   # servo B
        value = 2
        state_num = 5
    elif ADC.read(1) <= 30: 
        value = -2
        state_num = 4

    if ADC.read(2) <= 30: # servo C
        value = 3
        state_num = 8
    elif ADC.read(2)>= 210 :   # servo C
        value = -3 
        state_num = 9
    
    if servoD_mark == 1:
        if ADC.read(3) <= 30:   # servo D
            value = 4
            state_num = 10
        elif ADC.read(3) >= 210: 
            value = -4
            state_num = 11
    else:
        if ADC.read(3) <= 30:   # servo E
            value = 5
            state_num = 10
        elif ADC.read(3) >= 210: 
            value = -5
            state_num = 11
    if state_mark != state_num: # print state.
        print(state[state_num])
        state_mark = state_num
    return value

# 通过摇杆控制舵机
# Control the servo through the joystick.
def joystick_move_servo(value):
    global joystick_mark, joystick_button_mark
    if value != 0:
        joystick_mark = 1
    if value == 1:          # servo A
        scGear.singleServo(0, 1, 1) # (servo_ID, direction, speed)
        print(scGear.servoAngle())
    elif value == -1:
        scGear.singleServo(0, -1, 1)
        print(scGear.servoAngle())
    elif value == 2:        # servo B
        scGear.singleServo(1, 1, 1)
    elif value == -2:
        scGear.singleServo(1, -1, 1)
    elif value == 3:        # servo C
        scGear.singleServo(2, 1, 1)
    elif value == -3:
        scGear.singleServo(2, -1, 1)
    elif value == 4:        # servo D
        scGear.singleServo(3, 1, 1)
    elif value == -4:
        scGear.singleServo(3, -1, 1)
    elif value == 5:        # servo E
        scGear.singleServo(4, 1, 1)
    elif value == -5:
        scGear.singleServo(4, -1, 1)
    elif value == 6:
        scGear.planThreadingStart()
        scGear.angleUpdate()
        joystick_button_mark = 1
    elif value ==  -6:
        scGear.moveThreadingStop()
        joystick_button_mark = 0
    else:   # servo stop
        if joystick_mark == 1 and joystick_button_mark == 0:
            scGear.stopWiggle()
            joystick_mark = 0
    
def joystickControl():
    joystickSetup()
    while True:
        value = joystick()
        joystick_move_servo(value)
        time.sleep(0.05)

# 检测树莓派是否连接到网络
# Check if the Raspberry Pi is connected to the network.
def WiFi_check():
    try:
        s =socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        s.connect(("1.1.1.1",80))
        ipaddr_check=s.getsockname()[0]
        s.close()
        print(ipaddr_check)
    except:
        ap_threading=threading.Thread(target=ap_thread)   #Define a thread for data receiving
        ap_threading.setDaemon(True)                          #'True' means it is a front thread,it would close when the mainloop() closes
        ap_threading.start()                                  #Thread starts
        print("Raspberry Pi WiFi Turn On!")
        print("IP: 192.168.12.1")

async def check_permit(websocket):
    print("check_permit")
    while True:
        recv_str = await websocket.recv()
        cred_dict = recv_str.split(":")
        if cred_dict[0] == "admin" and cred_dict[1] == "123456":
            response_str = "congratulation, you have connect with server\r\nnow, you can do something else"
            await websocket.send(response_str)
            return True
async def recv_msg(websocket):
    print("recv_msg")
    while True:
        response = {
            'status': 'ok',
            'title': '',
            'data': None
        }
        data = ''
        data = await websocket.recv()
        try:
            data = json.loads(data)
        except Exception as e:
            print("Not A JSON")
        
        if not data:
            continue
        #print("data:", data)
        if data != 'get_info':
            print(data)
        if isinstance(data, str):
            robotCtrl(data, response)
            configInitAngle(data, response)
        
        if data == "get_info":
            response['title'] = 'get_info'
            response['data'] = [info.get_cpu_tempfunc(), info.get_cpu_use(), info.get_ram_info()]

        response = json.dumps(response)
        await websocket.send(response)

async def main_logic(websocket, path):
    await check_permit(websocket)
    await recv_msg(websocket)

if __name__ == "__main__":
    global flask_app
    flask_app = app.webapp()
    flask_app.startThread()

    joystickControlThreading=threading.Thread(target=joystickControl)
    joystickControlThreading.setDaemon(True)
    joystickControlThreading.start()

    while True:
        WiFi_check()
        try:
            start_server = websockets.serve(main_logic, '0.0.0.0', 8888)
            asyncio.get_event_loop().run_until_complete(start_server)
            print('waiting for connection...')
            break
        except Exception as e:
            print(e)
    try:
        asyncio.get_event_loop().run_forever()
    except Exception as e:
        print(e)          

    
        