# Little webserver to switch GPIO pins used as "output" pins (to switch relais or LEDs for example)
from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import os
import sys
import RPi.GPIO as GPIO

# Nothing below has to be changed.
argsArray = sys.argv
if len(argsArray) > 1:
    serverPort = int(argsArray[1])
else:
    serverPort = 80

hostName = os.popen('hostname -A').read().replace("\r","").replace("\n","").replace(" ","")
GPIO.setmode(GPIO.BOARD)

class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        path = self.path
        showUsageHints = False
        print ("Pfad: " + path)
        if (path[0:5] == "/gpio"):
            # HTTP parameters
            mode = path[6:9]
            pinNumber = int(path[10:12])
            if mode == 'GET' and len(path) >= 12:
                print("Mode: " + mode + ", GPIO-PIN: " + str(pinNumber))
                GPIO.setup(pinNumber, GPIO.OUT)
                self.wfile.write(bytes(str(GPIO.input(pinNumber)), "utf-8"))

            elif mode == 'SET' and len(path) >= 14:
                setAction = int(path[13:14])
                print("Mode: " + mode + ", GPIO-PIN: " + str(pinNumber) + ", Action: " + str(setAction))
                GPIO.setup(pinNumber, GPIO.OUT)
                if setAction == 1:
                    GPIO.output(pinNumber, GPIO.HIGH)
                    print ("Set PIN " + str(pinNumber) + " to HIGH")
                elif setAction == 0:
                    GPIO.output(pinNumber, GPIO.LOW)
                    print ("Set PIN " + str(pinNumber) + " to LOW")
                else:
                    showUsageHints = True
                if not showUsageHints:
                    self.wfile.write(bytes(str(setAction), "utf-8"))
            else:
                showUsageHints = True
        else:
            showUsageHints = True
        if showUsageHints:
            self.wfile.write(bytes("<html><head><title>switch-pi relais-switch webserver</title></head>", "utf-8"))
            self.wfile.write(bytes("<body>", "utf-8"))
            self.wfile.write(bytes("<p>Debug-Information: you requested: %s</p>" % self.path, "utf-8"))
            self.wfile.write(bytes("<h1>How to use this switch-pi web server</h1><p>Use this url to get the state of a GPIO PIN or to set a GPIO PIN to 1 or 0.</p>", "utf-8"))
            self.wfile.write(bytes("<h1>Usage</h1>", "utf-8"))
            self.wfile.write(bytes("Get state of a GPIO PIN DD (two digits): http://" + hostName + ":" + str(serverPort) + "/gpio/DD/GET</p> ", "utf-8"))
            self.wfile.write(bytes("Set state of a GPIO PIN DD (two digits) to HIGH: http://" + hostName + ":" + str(serverPort) + "/gpio/DD/SET/1</p> ", "utf-8"))
            self.wfile.write(bytes("Set state of a GPIO PIN DD (two digits) to LOW: http://" + hostName + ":" + str(serverPort) + "/gpio/DD/SET/0</p> ", "utf-8"))
            self.wfile.write(bytes("Please note: This script uses GPIO PINS in mode \"GPIO.setmode(GPIO.BOARD)\"</p> ", "utf-8"))
            self.wfile.write(bytes("</body></html>", "utf-8"))

if __name__ == "__main__":
    switchPiServer = HTTPServer((hostName, serverPort), MyServer)
    print("Started webserver at http://%s:%s" % (hostName, serverPort))

    try:
        switchPiServer.serve_forever()
    except KeyboardInterrupt:
        pass

    switchPiServer.server_close()
    print("Stopped webserver.")
    GPIO.cleanup()
    print("GPIO cleanup finished.")
