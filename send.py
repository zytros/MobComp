import sys
from os import name

import serial
import time
import threading


def rec():
    # read from the device’s serial port (should be done in a separate thread)
    message = ""

    while True:  # while not terminated
        try:
            byte = s.read(1)  # read one byte (blocks until data available or timeout reached)
            if len(byte) == 0:
                continue
            val = chr(byte[0])
            if val == '\n':  # if termination character reached
                print(message)  # print message
                message = ""  # reset message
            else:
                message = message + val  # concatenate the message
        except serial.SerialException:
            continue  # on timeout try to read again
        except KeyboardInterrupt:
            sys.exit()  # on ctrl-c terminate program


if name == 'main':
    port = input('COM port: ')
    mac = input('MAC address: ')
    dest = input('dest address: ')
    s = serial.Serial(port, 115200,
                      timeout=1)  # opens a serial port (resets the device!)  time.sleep(2) #give the device
    # some time to startup (2 seconds)
    time.sleep(2)

    # write to the device’s serial port
    s.write(str.encode("a[" + mac + "]\n"))  # set the device address to AB
    time.sleep(0.1)  # wait for settings to be applied
    s.write(str.encode("c[1,0,5]\n"))  # set number of retransmissions to 5
    time.sleep(0.1)  # wait for settings to be applied
    s.write(str.encode("c[0,1,30]\n"))  # set FEC threshold to 30 (apply FEC to packets with payload >= 30)
    time.sleep(0.1)  # wait for settings to be applied

    x = threading.Thread(target=rec)
    x.start()

    #
    #TODO: send correct data
    #

    def send(data):
        s.write(str.encode("m[" + data + "\0," + dest + "]\n"))
        print("sent "+str(len(data))+"bytes")
        time.sleep(len(data) * 0.005 + 0.1)

    oneByte = "a"
    tenBytes = "aaaaaaaaaa"
    twentyBytes = tenBytes + tenBytes
    fiftyBytes = twentyBytes + twentyBytes + tenBytes
    hundredBytes = fiftyBytes + fiftyBytes
    twohundredBytes = hundredBytes + hundredBytes

    def sendRound():
        send(oneByte)
        send(tenBytes)
        send(twentyBytes)
        send(fiftyBytes)
        send(hundredBytes)
        send(twentyBytes)
        time.sleep(5)


    while 1:
        msg = input('press any key to start new round')
        sendRound()