#messageを受信するノード
import utime
import socket
import _thread
import network
import urequests

import machine
from machine import Pin
from password import *

SSID_ESP = {'ESP_D49C9D','ESP_D374C5'}

wifiStatus = True
wifi = network.WLAN(network.STA_IF)

p2 = Pin(2, Pin.OUT)
red = Pin(13, Pin.OUT)
green = Pin(14, Pin.OUT)
blue = Pin(27, Pin.OUT)

port = 80

socket_to_KM = None
address = None

message = ''

buffer_size = 1024

def receiving():
    global host
    global port
    global socket_to_KM
    global address
    global message

    host = wifi.ifconfig()[2]
    try:
        sendSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        red.on()
        sendSocket.connect((host,port))
        red.off()
        sendSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)


        data = sendSocket.recv(buffer_size)
        send_count = int(data.decode())
        print('Number of chunks:', send_count)

        image_data = b""
        for i in range(send_count):
            chunk = sendSocket.recv(buffer_size)
            image_data += chunk
        
        with open('received_image.jpg', 'wb') as image_file:
            image_file.write(image_data)

        print("Image received and saved as 'received_image.jpg'.")

        print(f'received message: {message}')
        sendSocket.close()
    except Exception as e:
        print(e)
        pass

def wifiscan():
    global wifi
    wifiList = wifi.scan()
    wifiAPDict = []
    for wl in wifiList:
        if wl[0].decode("utf-8") != "":
            wifiAPDict.append(wl[0].decode("utf-8"))
    return wifiAPDict

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

def mkb():
    with open('received_image.jpg', 'rb') as image_file:
        image_data = image_file.read()
    return image_data

def toServer():
    image_data = mkb()
    url = 'http://192.168.100.140:5000/data'
    #data = {'name': 'image', 'image': image_data}
    files = {'image':('received_image.jpg',image_data)}
    print(files)

    #response = urequests.post(url, json=data)
    response = urequests.post(url, json=files)
    if response.status_code == 201:
        print('Data saved successfully')
    else:
        print('Failed to save data.')
    response.close()

def main():
    global wifi
    global message

    count = 0

    print('This is a tester node.')

    connect_lab_wifi()

        # print('errrr')
        # utime.sleep(2)
        # wifi.active(True)
        # connect_esp_wifi()
        # receiving()
        # utime.sleep(2)
        # wifi.disconnect()
        # p2.off()

        # connect_esp_wifi()
        # receiving()
        # utime.sleep(2)
        # wifi.disconnect()
        # utime.sleep(20)
        # p2.off()

if __name__ == "__main__":
    main()