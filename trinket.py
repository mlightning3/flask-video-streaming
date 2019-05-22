import serial
from multiprocessing import Process, Queue
from queue import Empty

##
# This handles talking to the trinket (or similar device connected over serial), providing way to read and write to it
# Also provides a Led class for drop-in replacement of Led controllers, but talks to Trinket instead
##

def serial_worker(serialCon, toTrinket, fromTrinket):
    if serialCon.is_open:
        stop = False
        while stop is not True:
            if serialCon.in_waiting > 0:
                fromTrinket.put(serialCon.readline()) # Add message from Trinket to queue to be read by main process
            if toTrinket.empty() is False:
                message = None
                try:
                    message = toTrinket.get_nowait() # Read message from main process
                except Empty:
                    message = None
                if message is not None:
                    if message == 'stop':
                        stop = True
                    else:
                        serialCon.write(message.encode('latin-1'))
        serialCon.close()


class Trinket(object):
    tty = '/dev/serial0'
    baud = 9600
    ser = None
    trinket_process = None
    toTinket = Queue()
    fromTrinket = Queue()


    ## Creates a Trinket object
    #
    # @param tty A string to the tty device we should listen on (default is '/dev/serial0')
    # @param baud The rate of data transfer as an int (default is 9600)
    def __init__(self, tty='/dev/serial0', baud=9600):
        try:
            Trinket.tty = tty
            Trinket.baud = baud
            Trinket.ser = serial.Serial(self.tty, self.baud, timeout=1)  # This defaults to /dev/serial0 at 9600 baud if nothing was passed in
        except ValueError as ve:  # Some value we passed in was bad
            print(ve)
            exit(2)
        except serial.SerialException as se:  # Unable to find tty device
            print(se)
            exit(2)
        Trinket.add_process(self)

    ## Gets latest raw data from Trinket
    #
    def get_data(self):
        message = ''
        try:
            message = Trinket.fromTrinket.get_nowait().decode('latin-1')
        except Empty:
            message = ''
        return message

    ## Sends string to Trinket
    #
    # @param data String we wish to send to Trinket
    def send_message(self, data):
        Trinket.toTinket.put(str(data))

    ## Closes connection to Trinket
    #
    def close(self):
        Trinket.toTinket.put('stop')
        Trinket.trinket_process.join()
        Trinket.trinket_process = None

    ## Builds new worker process
    #
    def add_process(self):
        if Trinket.trinket_process is None:
            Trinket.toTrinket = Queue()
            Trinket.fromTrinket = Queue()
            Trinket.trinket_process = Process(target=serial_worker, args=(Trinket.ser, Trinket.toTinket, Trinket.fromTrinket,))
            Trinket.trinket_process.start()


class Led(object):
    trinket = None
    brightness = 'FF'
    prev_brightness = brightness
    White = 'FFFFFF'
    Off = '000000'
    color = 'FFFFFF'
    prev_color = color

    ## Creates a Led object
    #
    # @param trinket A trinket object with neopixels attached
    def __init__(self, trinket):
        Led.trinket = trinket

    ## Changes the color of neopixels
    #
    # This will go through all the neopixels and change their color
    # @param color A string describing the color we want
    def set_color(self, color):
        Led.prev_color = Led.color
        Led.color = color
        Led.update_color(self)

    ## Powers on and off the neopixels
    #
    # Switches the color between Off and the previous color (unless it was also off, which then defaults to white)
    # @param status True or False if we want the neopixel on
    def power_led(self, status):
        if status == "True" or status == "true":
            if Led.prev_color == Led.Off:
                Led.color = Led.White
            else:
                Led.color = Led.prev_color
            if Led.prev_brightness == '00':
                Led.brightness = 'FF'
            else:
                Led.brightness = Led.prev_brightness
        elif status == "False" or status == "false":
            Led.prev_color = Led.color
            Led.color = Led.Off
            Led.prev_brightness = Led.brightness
            Led.brightness = '00'
        Led.update_color(self)

    ## Sets brightness of neopixels
    #
    # Changes the brightness of all the neopixels
    # @param value A number from 0 to 255 (all other are ignored)
    def set_brightness(self, value):
        if value < 256 and value > -1:
            tempvalue = hex(value)
            tempvalue = tempvalue[2:]
            if len(tempvalue) is 1:
                tempvalue = '0' + tempvalue
            Led.brightness = tempvalue
            Led.update_color(self)

    ## Builds a Color for use with neopixels (API compatability)
    #
    # This is only here for API comparability with other Led classes, it only returns the string you put in if it is valid
    #
    # Builds a Color based on the hex values encoded in a string of at least length 6
    # An example: FFFFFF would make a Color that is bright white
    # A string that is too short will give a Color of black
    # @param hexstring A string with the hexcodes for a color (format: RRGGBB)
    def build_color(self, hexstring):
        tempcolor = Led.Off
        if len(hexstring) >= 6:
            tempcolor = hexstring[:6]
        return tempcolor

    ## Updates the color based on the current brightness
    #
    # This won't change the values inside color or brightness, just sends the adjusted colors
    # If the trinket is changed to calculate the proper brightness, this function isn't needed
    def update_color(self):
        brightness = int(Led.brightness, 16) / 255
        red = int(Led.color[:2], 16) * brightness
        green = int(Led.color[2:4], 16) * brightness
        blue = int(Led.color[4:6], 16) * brightness
        red = hex(int(red))
        green = hex(int(green))
        blue = hex(int(blue))
        red = red[2:]
        if len(red) is 1:
            red = '0' + red
        green = green[2:]
        if len(green) is 1:
            green = '0' + green
        blue = blue[2:]
        if len(blue) is 1:
            blue = '0' + blue
        message = red + green + blue + Led.brightness
        Led.trinket.send_message(message)
