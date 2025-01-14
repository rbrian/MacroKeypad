#TeachMe PCB Rev 2 Class
#Bring up hardware, skull keypad - Jesse Robinson
#11/8/2021

import time
import busio
import board
import rotaryio
import digitalio
import neopixel
from digitalio import DigitalInOut, Direction, Pull
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode
#import adafruit_veml7700

i2c = busio.I2C(board.GP21, board.GP20)

# Update this to match the number of NeoPixel LEDs connected to your board.
num_pixels = 10

brightnessSteps = 50
pixelBrightness = brightnessSteps/2

pixels = neopixel.NeoPixel(board.GP19, num_pixels)
pixels.brightness = float(pixelBrightness) / brightnessSteps

spi = busio.SPI(clock=board.GP26, MOSI=board.GP27)
latch = digitalio.DigitalInOut(board.GP28)
latch.direction = digitalio.Direction.OUTPUT
latch.switch_to_output(True)
latch.value = False

RED = (255, 0, 0)
YELLOW = (255, 150, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
PURPLE = (180, 0, 255)

kbd = Keyboard(usb_hid.devices)
cc = ConsumerControl(usb_hid.devices)

# list of pins to use (skipping GP15 on Pico because it's funky)
pins = [
    board.GP1,
    board.GP2,
    board.GP3,
    board.GP4,
    board.GP5,
    board.GP6,
    board.GP7,
    board.GP8,
    board.GP9,
    board.GP10,
    board.GP11,
    board.GP12,
]

MEDIA = 1
KEY = 2

keymap = {
    (0): (KEY, [Keycode.ONE]),
    (1): (KEY, [Keycode.TWO]),
    (2): (KEY, [Keycode.THREE]),
    (3): (KEY, [Keycode.FOUR]),
    (4): (KEY, [Keycode.FIVE]),
    (5): (KEY, [Keycode.SIX]),
    (6): (KEY, [Keycode.SEVEN]),
    (7): (KEY, [Keycode.EIGHT]),
    (8): (KEY, [Keycode.NINE]),
    (9): (KEY, [Keycode.ZERO]),
    (10): (KEY, [Keycode.X]), #unused
    (11): (KEY, [Keycode.Y]), #unused
   }
switches = [0, 1, 2, 3, 4, 5, 6,
            7, 8, 9, 10, 11]

for i in range(10):
    switches[i] = DigitalInOut(pins[i])
    switches[i].direction = Direction.INPUT
    switches[i].pull = Pull.UP

switches[10] = digitalio.DigitalInOut(board.GP11)
switches[11] = digitalio.DigitalInOut(board.GP12)

switch_state = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

leftEncoder = rotaryio.IncrementalEncoder(board.GP17, board.GP18)
leftEncoder_last_position = leftEncoder.position

rightEncoder = rotaryio.IncrementalEncoder(board.GP14, board.GP15)
rightEncoder_last_position = rightEncoder.position

while not spi.try_lock():
    pass

while not i2c.try_lock():
    pass
#veml7700 = adafruit_veml7700.VEML7700(i2c)

#print("Ambient light:", veml7700.light)

trackColor = 1

def ledChange():
    global trackColor

    if (trackColor == 0):
        pixels.fill(RED)
    elif (trackColor == 1):
        pixels.fill(YELLOW)
    elif (trackColor == 2):
        pixels.fill(GREEN)
    elif (trackColor == 3):
        pixels.fill(CYAN)
    elif (trackColor == 4):
        pixels.fill(BLUE)    
    elif (trackColor == 5):
        pixels.fill(PURPLE)    
    else:
        trackColor = 0
        pixels.fill(RED)

ledChange()

spi.configure(baudrate=5000000, phase=0, polarity=0)
spi.write(bytes([0x00]))
latch.value = True
latch.value = False
time.sleep(1)
spi.write(bytes([0xF6]))
latch.value = True
latch.value = False

while True:
    for button in range(10):
        if switch_state[button] == 0:
            if not switches[button].value:
                try:
                    if keymap[button][0] == KEY:
                        kbd.press(*keymap[button][1])
                    else:
                        cc.send(keymap[button][1])
                except ValueError:  # deals w six key limit
                    pass
                switch_state[button] = 1

        if switch_state[button] == 1:
            if switches[button].value:
                try:
                    if keymap[button][0] == KEY:
                        kbd.release(*keymap[button][1])

                except ValueError:
                    pass
                switch_state[button] = 0

    button = 10
    if switch_state[button] == 0:
        if switches[button].value:
            try:
                if keymap[button][0] == KEY:
                    pass
                    trackColor = trackColor + 1
                    ledChange()
                    #kbd.press(*keymap[button][1])
                else:
                    pass
                    #cc.send(keymap[button][1])
            except ValueError:  # deals w six key limit
                pass
            switch_state[button] = 1

    if switch_state[button] == 1:
        if not switches[button].value:
            try:
                if keymap[button][0] == KEY:
                    pass 
                    #kbd.release(*keymap[button][1])
            except ValueError:
                pass
            switch_state[button] = 0

    button = 11
    if switch_state[button] == 0:
        if switches[button].value:
            try:
                if keymap[button][0] == KEY:
                    pass
                    cc.send(ConsumerControlCode.PLAY_PAUSE)
                    #kbd.press(*keymap[button][1])
                else:
                    pass
                    #cc.send(keymap[button][1])
            except ValueError:  # deals w six key limit
                pass
            switch_state[button] = 1

    if switch_state[button] == 1:
        if not switches[button].value:
            try:
                if keymap[button][0] == KEY:
                    pass
                    #kbd.release(*keymap[button][1])
            except ValueError:
                pass
            switch_state[button] = 0

    current_position = leftEncoder.position
    position_change = current_position - leftEncoder_last_position
    if position_change > 0:
        for _ in range(position_change):
            if (pixelBrightness < brightnessSteps):
                pixelBrightness = pixelBrightness + 1
        #print(pixelBrightness)
        pixels.brightness = float(pixelBrightness) / brightnessSteps
    elif position_change < 0:
        for _ in range(-position_change):
            if (pixelBrightness > 0):
                pixelBrightness = pixelBrightness - 1
        #print(pixelBrightness)
        pixels.brightness = float(pixelBrightness) / brightnessSteps
    leftEncoder_last_position = current_position

    current_position = rightEncoder.position
    position_change = current_position - rightEncoder_last_position
    if position_change > 0:
        for _ in range(position_change):
            cc.send(ConsumerControlCode.VOLUME_INCREMENT)
        #print(current_position)
    elif position_change < 0:
        for _ in range(-position_change):
            cc.send(ConsumerControlCode.VOLUME_DECREMENT)
        #print(current_position)
    rightEncoder_last_position = current_position

    time.sleep(0.02)  # debounce
