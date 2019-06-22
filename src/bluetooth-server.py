import os
import subprocess
import select
import serial
import time
import json
import re

wpa_supplicant_conf = "/etc/wpa_supplicant/wpa_supplicant.conf"
sudo_mode = "sudo "
 
class SerialComm:
    def __init__(self):
        self.port = serial.Serial("/dev/rfcomm0", baudrate=9600, timeout=1)
 
    def read_serial(self):
        res = self.port.read(50)
        if len(res):
            return res.splitlines()
        else:
            return []
 
    def send_serial(self, text):
        self.port.write(text)

    def isValidCommand(self, command, validCommand):
        if command in validCommand:
            if re.match("^[a-zA-Z0-9. -]+$",command):
                return True
            
        return False

class ShellWrapper:
    def __init__(self):
        self.ps = subprocess.Popen(['bash'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
 
    def execute_command(self, command):
        self.ps.stdin.write(command + "\n")
 
    def get_output(self):
        timeout = False
        time_limit = .5
        lines = []
        while not timeout:
            poll_result = select.select([self.ps.stdout, self.ps.stderr], [], [], time_limit)[0]
            if len(poll_result):

                for p in poll_result:
                    lines.append(p.readline())              
            else:
                timeout = True
            
        if(len(lines)):
            return lines
        else:
            return None
 
 
def main():
    shell = ShellWrapper()
    invalidCommand = ['clear','head','sudo','nano','touch','vim']
    validCommand = ['passwd', 'hostname', 'reboot', 'wifi']
    ble_comm = None
    isConnected = False
    
    while True:
        try:
            ble_comm = SerialComm()
            out = ble_comm.read_serial()
            for ble_line in out:
                print(out)
                ble_command = ble_line.split(' ', 1)[0]

                if ble_comm.isValidCommand(ble_command, validCommand):
                    
                    shell.execute_command("/home/pi/bin/"+ble_line)
                    shell_out = shell.get_output()
                    if shell_out != None:
                        for l in shell_out:
                            print(l)
                            ble_comm.send_serial(l)
                    else:
                        ble_comm.send_serial("command '" + ble_line + "' return nothing ")
                else:
                  ble_comm.send_serial("command '" + ble_line + "' not support ")  
          
        except serial.SerialException:
            print("waiting for connection")
            ble_comm = None
            isConnected = False
            time.sleep(1)
            
if __name__ == "__main__":
    main()
