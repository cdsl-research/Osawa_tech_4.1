import utime
import socket
import _thread
import network
import urequests
from machine import Pin
from password import *

SSID_NAME_LAB = ["CDSL-A910-11n"]
SSID_ESP = {"ESP_D38A19"} #ノードB

p2 = Pin(2,Pin.OUT)
red = Pin(13, Pin.OUT)
blue = Pin(4, Pin.OUT)
green = Pin(5, Pin.OUT)

port = 80

count = 1
url = None
sensor_data = "A00000000"
A_data = str(count) + "," + sensor_data
B_data = ""
listenSocket = None

def init():
    global listenSocket

    listenSocket = socket.socket()
    listenSocket.bind(("",port))
    listenSocket.listen(5)
    listenSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

def A():
    global listenSocket
    global B_data
    global port

    while True:
        connection, client = listenSocket.accept()
        try:
            print("client connected", client)
            B_data = connection.recv(1024).decode()
            print(B_data)
        except Exception as e:
            print(e)
            pass
        finally:
            connection.close()
            break

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
                    #connect_esp_wifi()

def toServer():
    global url
    global B_data
    global A_data

    A_data = str(count) + "," + sensor_data

    url = "http://192.168.100.144/osawa/receive.php"
    sendData = {
                "A_data" : A_data,
                "A_id" : "ESP-A",
                "B_data" : B_data,
                "B_id": "ESP-B"
            }

    url += "?"

    for sdk,sdv in sendData.items():
        url += sdk + "=" + sdv + "&"
    print(url)
    res = urequests.get(url)
    print("サーバからのステータスコード：", res.status_code)
    res.close()

def ap_mode():
    global ap
    ap = network.WLAN(network.AP_IF) #アクセスポイントのインターフェースを作成
    # ap.config(ssid = "ESP-AP") #アクセスポイントのSSIDを設定
    # ap.config(maxclients = 1) #ネットワークに接続できるクライアント数

    ap.active(True) #インターフェースアクティブ化

    green.on()
    config = ap.ifconfig()

    print("enabled ap mode")
    print(config)

def ap_off():
    ap.active(False)
    green.off()

def main():
    global wifi
    global count
    global B_data
    init()
    while True:
        wifi.active(True)
        ap_mode()
        A()
        ap_off()
        connect_lab_wifi()
        try:
            toServer()
        except Exception as e:
            pass
        wifi.disconnect()
        wifi.active(False)
        p2.off()
        count += 1
        B_data = ""
        print(count)
        utime.sleep(30)


if __name__ == "__main__":
    _thread.start_new_thread(main,())



