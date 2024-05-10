#!/usr/bin/python3
# File name   : setup.py
# Author      : Adeept Devin
# Date        : 2022/7/12

import os
import time

curpath = os.path.realpath(__file__)
thisPath = "/" + os.path.dirname(curpath)

def replace_num(file,initial,new_num):
    newline=""
    str_num=str(new_num)
    with open(file,"r") as f:
        for line in f.readlines():
            if(line.find(initial) == 0):
                line = (str_num+'\n')
            newline += line
    with open(file,"w") as f:
        f.writelines(newline)



def check_rpi_model():
    _, result = run_command("cat /proc/device-tree/model |awk '{print $3}'")
    result = result.strip()
    if result == '3':
        return int(3)
    elif result == '4':
        return int(4)
    else:
        return None

def run_command(cmd=""):
    import subprocess
    p = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    result = p.stdout.read().decode('utf-8')
    status = p.poll()
    return status, result

def check_raspbain_version():
    _, result = run_command("cat /etc/debian_version|awk -F. '{print $1}'")
    return int(result.strip())

def check_python_version():
    import sys
    major = int(sys.version_info.major)
    minor = int(sys.version_info.minor)
    micro = int(sys.version_info.micro)
    return major, minor, micro

def check_os_bit():
    '''
    # import platform
    # machine_type = platform.machine() 
    latest bullseye uses a 64-bit kernel
    This method is no longer applicable, the latest raspbian will uses 64-bit kernel 
    (kernel 6.1.x) by default, "uname -m" shows "aarch64", 
    but the system is still 32-bit.
    '''
    _ , os_bit = run_command("getconf LONG_BIT")
    return int(os_bit)



commands_apt = [
    "sudo apt-get update",
    "sudo apt-get purge -y wolfram-engine",
    # "sudo apt-get purge -y libreoffice*",
    "sudo apt-get -y clean",
    "sudo apt-get -y autoremove",
    # "sudo apt-get install -y python-dev python-pip libfreetype6-dev libjpeg-dev build-essential",
    "sudo apt-get install -y libfreetype6-dev libjpeg-dev build-essential",
    "sudo apt-get install -y i2c-tools",
    "sudo apt-get install -y python3-smbus",
    # "sudo apt-get install -y libjasper-dev",
    "sudo apt-get install -y libatlas-base-dev",
    "sudo apt-get install -y libgstreamer1.0-0"
]
mark_apt = 0
for x in range(3):
    for command in commands_apt:
        if os.system(command) != 0:
            print("Error running installation step apt")
            mark_apt = 1
    if mark_apt == 0:
        break


commands_pip_1 = [
    "sudo pip3 install -U pip",
    "sudo pip3 install RPi.GPIO",
    "sudo -H pip3 install --upgrade luma.oled",
    "sudo pip3 install rpi_ws281x",
    "sudo pip3 install mpu6050-raspberrypi",
    "sudo pip3 install flask",
    "sudo pip3 install flask_cors",
    "sudo pip3 install websockets",
    "sudo pip3 install adafruit-circuitpython-motor",
    "sudo pip3 install adafruit-circuitpython-pca9685"
]
commands_pip_2 = [
    "sudo pip3 install -U pip --break-system-packages",
    "sudo pip3 install RPi.GPIO --break-system-packages",
    "sudo -H pip3 install --upgrade luma.oled --break-system-packages",
    "sudo pip3 install rpi_ws281x --break-system-packages",
    "sudo pip3 install mpu6050-raspberrypi --break-system-packages",
    "sudo pip3 install flask --break-system-packages",
    "sudo pip3 install flask_cors --break-system-packages",
    "sudo pip3 install websockets --break-system-packages",
    "sudo pip3 install adafruit-circuitpython-motor --break-system-packages",
    "sudo pip3 install adafruit-circuitpython-pca9685 --break-system-packages"
]

mark_pip = 0
OS_version = check_raspbain_version()
if OS_version <= 11:
    for x in range(3):
        for command in commands_pip_1:
            if os.system(command) != 0:
                print("Error running installation step pip")
                mark_pip = 1
        if mark_pip == 0:
            break
else:
    for x in range(3):
        for command in commands_pip_2:
            if os.system(command) != 0:
                print("Error running installation step pip")
                mark_pip = 1
        if mark_pip == 0:
            break


commands_2 = [
    "sudo apt-get -y install libhdf5-dev libatlas-base-dev",
    "sudo git clone https://github.com/oblique/create_ap",
    "cd " + thisPath + "/create_ap && sudo make install",
    "cd //home/pi/create_ap && sudo make install",
    "sudo apt-get install -y util-linux procps hostapd iproute2 iw haveged dnsmasq"
]

mark_2 = 0
for x in range(3):
    for command in commands_2:
        if os.system(command) != 0:
            print("Error running installation step 2")
            mark_2 = 1
    if mark_2 == 0:
        break

try:
    replace_num("/boot/config.txt", '#dtparam=i2c_arm=on','dtparam=i2c_arm=on\nstart_x=1\n')
except:
    print('Error updating boot config to enable i2c. Please try again.')

try:
    os.system('sudo touch //home/pi/startup.sh')
    with open("//home/pi/startup.sh",'w') as file_to_write:
        #you can choose how to control the robot
        file_to_write.write("#!/bin/sh\nsudo python3 " + thisPath + "/server/webServer.py")
#       file_to_write.write("#!/bin/sh\nsudo python3 " + thisPath + "/server/server.py")
except:
    pass

os.system('sudo chmod 777 //home/pi/startup.sh')

replace_num('/etc/rc.local','fi','fi\n//home/pi/startup.sh start')

# try:
#     os.system("sudo cp -f //home/pi/adeept_adr029/server/config.txt //etc/config.txt")
# except:
#     os.system("sudo cp -f "+ thisPath  +"/adeept_rasptank/server/config.txt //etc/config.txt")
print('The program in Raspberry Pi has been installed, disconnected and restarted. \nYou can now power off the Raspberry Pi to install the camera and driver board (Robot HAT). \nAfter turning on again, the Raspberry Pi will automatically run the program to set the servos port signal to turn the servos to the middle position, which is convenient for mechanical assembly.')
print('restarting...')
# os.system("sudo reboot")
