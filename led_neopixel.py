from neopixel import *

##
# This class wraps up all the details of controlling neopixles
##

class Led(object):
    # Things needed to set up neopixel properly
    LED_COUNT = 1
    LED_PIN = 18
    LED_FREQ = 800000
    LED_DMA = 10
    LED_INVERT = False
    LED_CHANNEL = 0
    # Things that won't change
    LED_STRIP = 0 # Holds our neopixel object
    White = Color(127, 127, 127)
    Blue = Color(0, 255, 0)
    Off = Color(0, 0, 0)
    # Things that will be changed during use
    brightness = 255
    color = White
    prev_color = White

    ## Builds an Led object
    #
    def __init__(self, led_count=1, led_pin=18, led_channel=0):
        Led.LED_COUNT = led_count
        Led.LED_PIN = led_pin
        Led.LED_CHANNEL = led_channel
        Led.LED_STRIP = Adafruit_NeoPixel(Led.LED_COUNT, Led.LED_PIN, Led.LED_FREQ, Led.LED_DMA, Led.LED_INVERT, Led.brightness, Led.LED_CHANNEL)
        Led.LED_STRIP.begin()

    ## Changes the color of neopixels
    #
    # This will go through all the neopixels and change their color
    # @param color A Color object describing the color we want
    def set_color(self, color):
        Led.prev_color = Led.color
        Led.color = color
        for i in range(Led.LED_COUNT):
            Led.LED_STRIP.setPixelColor(i, color)
            Led.LED_STRIP.show()

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
        Led.set_color(self, tempcolor)

    ## Shows blue light
    #
    # Changes between blue and white light
    # @param status True or False if we want blue light
    def show_blue(self, status):
        tempcolor = Led.Blue
        if status == "False" or status == "false":
            if Led.prev_color == Led.Off:
                tempcolor = Led.White
            else:
                tempcolor = Led.prev_color
        Led.set_color(self, tempcolor)

    ## Sets brightness of neopixels
    #
    # Changes the brightness of all the neopixels
    # @param value A number from 0 to 255 (all other are ignored)
    def set_brightness(self, value):
        if value < 256 and value > -1:
            Led.brightness = value
            Led.LED_STRIP.setBrightness(Led.brightness)
            Led.LED_STRIP.show()

    ## Builds a Color for use with neopixels
    #
    # Builds a Color based on the hex values encoded in a string of at least length 6
    # An example: FFFFFF would make a Color that is bright white
    # A string that is too short will give a Color of black
    # @param hexstring A string with the hexcodes for a color
    def build_color(self, hexstring):
        tempcolor = Led.Off
        if len(hexstring) >= 6:
            tempcolor = Color(int(hexstring[0:2], 16), int(hexstring[2:4], 16), int(hexstring[4:6], 16))
        return tempcolor