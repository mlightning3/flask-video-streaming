import serial
import threading

##
# This handles talking to the trinket (or similar device connected over serial), providing way to read and write to it
# Also provides a Led class for drop-in replacement of Led controllers, but talks to Trinket instead
##

class Trinket(object):
    tty = '/dev/ttyUSB0'
    baud = 9600
    ser = None
    trinket_thread = None
    data = 0
    message = None
    stop = False


    ## Creates a Trinket object
    #
    # @param tty A string to the tty device we should listen on (default is '/dev/ttyUSB0')
    # @param baud The rate of data transfer as an int (default is 9600)
    def __init__(self, tty='/dev/ttyUSB0', baud=9600):
        try:
            Trinket.ser = serial.Serial(tty, baud, timeout=1)  # This defaults to /dev/ttyUSB0 at 9600 baud if nothing was passed in
        except ValueError as ve:  # Some value we passed in was bad
            print(ve)
            exit(2)
        except serial.SerialException as se:  # Unable to find tty device
            print(se)
            exit(2)
        if Trinket.trinket_thread is None:
            Trinket.trinket_thread = threading.Thread(target=self._thread)
            Trinket.trinket_thread.start()

    ## Gets latest raw data from Trinket
    #
    def get_data(self):
        return Trinket.data

    ## Sends string to Trinket
    #
    # @param data String we wish to send to Trinket
    def send_message(self, data):
        Trinket.message = str(data)

    ## Closes connection to Trinket
    #
    def close(self):
        Trinket.stop = True

    ## Handles reading and writign to trinket
    #
    @classmethod
    def _thread(cls):
        while cls.stop is not True:
            cls.data = cls.ser.readline()
            if cls.message is not None:
                cls.write(cls.message.encode('latin-1'))
                cls.message = None
        cls.ser.close()

class Led(object):
    trinket = None
    brightness = 255
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
        Led.trinket.send_message(color + Led.brightness)

    ## Powers on and off the neopixels
    #
    # Changes the color between white and off
    # @param status True or False if we want the neopixel on
    def power_led(self, status):
        tempcolor = Led.prev_color
        if status == "True" or status == "true":
            if tempcolor == Led.Off:
                tempcolor = Led.White
        elif status == "False" or status == "false":
            tempcolor = Led.Off
        Led.trinket.send_message(tempcolor + Led.brightness)

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
            Led.trinket.send_message(Led.color + Led.brightness)

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