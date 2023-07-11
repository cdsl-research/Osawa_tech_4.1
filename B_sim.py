import utime
import socket
import _thread
import network
import urequests
from machine import Pin
from password import *

SSID_NAME_LAB = ["CDSL-A910-11n"]
SSID_ESP = {"ESP_D356F5"} #TODO　SSID入れる

p2 = Pin(2,Pin.OUT)
red = Pin(13, Pin.OUT)
blue = Pin(4, Pin.OUT)
green = Pin(5, Pin.OUT)

port = 80

count = 1
sensor_data = "B00000000"
B_data = str(count) + "," + sensor_data

def init():
    global s
    s = socket.socket()

def B():
    global s
    global port
    host = wifi.ifconfig()[2]
    B_data = str(count) + "," + sensor_data

    try:
        s.connect((host,port))
        data = B_data
        s.send(data.encode())
        print(f"sent data: {B_data}")
    finally:
        s.close()

def wifiscan():
    global wifi
    wifiList = wifi.scan()
    wifiAPDict = []
    for wl in wifiList:
        if wl[0].decode("utf-8") != "":
            wifiAPDict.append(wl[0].decode("utf-8"))
    return wifiAPDict

def connect_lab_wifi(timeout = 10):
    global wifi
    if wifi.ifconfig()[0].split(".")[0] == "192":
        wifi.disconnect()
    else:
        pass
    
    endFlag = False
    wifiName = wifiscan()
    print(wifiName)

    for wn in wifiName:
        if wn in SSID_NAME_LAB:
            print(f"[{wn}]に接続します")
            wifi.connect(wn, lab_wifi_pass)
            while True:
                
                if wifi.ifconfig()[0].split(".")[0] == "192":
                    p2.on()
                    endFlag = True
                    print("----  wifi is connected -----")
                    print(f"----[{wifi.ifconfig()[0]}]に接続----")
                    webrepl.start(password = webrepl_pass)
                    break
                else:
                    utime.sleep(1)
            if endFlag == True:
                break
        if endFlag == True:
            break

def connect_esp_wifi(timeout = 10):
    global wifi
    if wifi.ifconfig()[0].split(".")[0] == "192":
        wifi.disconnect()
    else:
        pass
    
    wifiName = wifiscan()
    #print(wifiName) #羅列が煩わしいので，デバッグ時は#外す

    for wn in wifiName:
        if wn in SSID_ESP:
            print(f"---ESPのWi-Fi[{wn}]に接続します---")
            wifi.connect(wn)
            while True:

                if wifi.ifconfig()[0].split(".")[0] == "192":
                    p2.on()
                    
                    print("---- wifi is connected ----")
                    print(f"----[{wifi.ifconfig()[0]}]に接続----")
                    return True

                else:
                    utime.sleep(1)

def main():
    global count
    global B_data
    init()
    while True:
        wifi.active(True)
        connect_esp_wifi()
        B()
        wifi.disconnect()
        p2.off()
        wifi.active(False)
        count += 1
        print("Next count: ",count)
        utime.sleep(30)

if __name__ == "__main__" :
    main()