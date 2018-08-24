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
        for i in range(Led.LED_COUNT):
            Led.LED_STRIP.setPixelColor(i, color)
            Led.LED_STRIP.show()

    ## Powers on and off the neopixels
    #
    # Changes the color between white and off
    # @param status True or False if we want the neopixel on
    def power_led(self, status):
        if status == "True" or status == "true":
            Led.set_color(self, Led.White)
        elif status == "False" or status == "false":
            Led.set_color(self, Led.Off)

    ## Shows blue light
    #
    # Changes between blue and white light
    # @param status True or False if we want blue light
    def show_blue(self, status):
        if status == "True" or status == "true":
            Led.set_color(self, Led.Blue)
        elif status == "False" or status == "false":
            Led.set_color(self, Led.White)

    ## Sets brightness of neopixels
    #
    # Changes the brightness of all the neopixels
    # @param value A number from 0 to 255 (all other are ignored)
    def set_brightness(self, value):
        if value < 256 and value > -1:
            Led.brightness = value
            Led.LED_STRIP.setBrightness(Led.brightness)
            Led.LED_STRIP.show()