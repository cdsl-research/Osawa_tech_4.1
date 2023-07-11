#APモードを起動する，送信側ノード

import socket
import _thread
import network
import machine
from machine import Pin
import utime
from password import *

wifiStatus = True
wifi = network.WLAN(network.STA_IF)

p2 = Pin(2, Pin.OUT)
red = Pin(13, Pin.OUT)
green = Pin(14, Pin.OUT)
blue = Pin(27, Pin.OUT)

port = 80

socket_to_KH = None
address = None
s = None

message = "How's it going?"

buffer_size = 1024

def init():
    global s
    s = socket.socket()
    s.bind(("",port))
    s.listen(5)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

def sending():
    global port
    global socket_to_KH
    global address
    global message
    global s

    while True:
        connection, client = s.accept()

        with open('material.jpeg', 'rb') as image_file:
            image_data = image_file.read()
        try:
            print(f'----Client {client} connected----')

            image_size = len(image_data)
            send_count = (image_size // buffer_size) + 1

            connection.send(str(send_count).encode())

            for i in range(send_count):
                start = i * buffer_size
                end = min((i + 1) * buffer_size, image_size)
                chunk = image_data[start:end]
                connection.sendall(chunk)

            print('Number of chunks:', send_count)
            utime.sleep(2)
        finally:
            connection.close()
            print('connection is closed')
            break

def ap_mode():
    global ap
    ap = network.WLAN(network.AP_IF)

    ap.active(True)
    green.on()
    print('enabled ap mode')
    config = ap.ifconfig()
    print(config)

def ap_off():
    ap.active(False)
    green.off()

def main():
    print('This is a sender node.')
    init()
    while True:
        wifi.active(True)
        ap_mode()
        utime.sleep(1)
        sending()
        ap_off()
        wifi.active(False)
        utime.sleep(30)

if __name__ == '__main__':
    main()