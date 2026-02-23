from machine import Pin
from neopixel import NeoPixel
from hcsr04 import HCSR04
import time
import random

# BUTTON

button = Pin(5, Pin.IN, Pin.PULL_UP)

# GAME SENSORS

ir = Pin(21, Pin.IN)        # Yellow
touch = Pin(19, Pin.IN)     # Blue
shock = Pin(18, Pin.IN)     # Green

# ULTRASONIC

ultra = HCSR04(trigger_pin=32, echo_pin=33)

# NEOPIXEL

dataPin = 23
pixels = 16
np = NeoPixel(Pin(dataPin, Pin.OUT), pixels)

# CLEAR function

def clear():
    for i in range(pixels):
        np[i] = (0,0,0)
    np.write()

# WAIT FOR START

def wait_for_start():

    print("Stand at least 30cm away")

    while True:
        distance = ultra.distance_cm()
        print("Distance:", distance)

        if distance < 30:
            print("Too close to start")
            np.fill((255,165,0))
            np.write()
        else:
            print("Safe distance - Press button")
            np.fill((0,255,0))
            np.write()

            if button.value() == 0:
                print("Game starting")
                clear()
                break

        time.sleep(0.5)

# PAUSE FUNCTION

def check_pause():

    if ultra.distance_cm() < 5:
        print("Paused - Player too close")

        np.fill((255,255,0))
        np.write()

        while ultra.distance_cm() < 5:
            time.sleep(0.2)

        print("Resuming game")
        clear()

# RAINBOW SPIN

def rainbow_spin(speed):

    print("Spinning rainbow, speed:", speed)

    np[0]  = (255,165,0)
    np[1]  = (255,127,0)
    np[2]  = (255,255,0)
    np[3]  = (0,255,0)
    np[4]  = (0,0,255)
    np[5]  = (75,0,130)
    np[6]  = (148,0,211)
    np[7]  = (255,165,0)
    np[8]  = (255,127,0)
    np[9]  = (255,255,0)
    np[10] = (0,255,0)
    np[11] = (0,0,255)
    np[12] = (75,0,130)
    np[13] = (148,0,211)
    np[14] = (255,165,0)
    np[15] = (255,127,0)

    np.write()

    for r in range(pixels):
        last = np[15]
        for i in range(15,0,-1):
            np[i] = np[i-1]
        np[0] = last
        np.write()
        time.sleep(speed)


# COUNTDOWN (RED then YELLOW then GREEN)

def countdown():

    print("3")
    np.fill((255,0,0))  # RED
    np.write()
    time.sleep(1)
    clear()

    print("2")
    np.fill((255,255,0))  # YELLOW
    np.write()
    time.sleep(1)
    clear()

    print("1")
    np.fill((0,255,0))  # GREEN
    np.write()
    time.sleep(1)
    clear()

    print("GO")

# WIN Function

def rainbow():

    print("YOU WIN")
    np.fill((0,255,0))
    np.write()
    time.sleep(3)
    clear()

# MAIN GAME LOOP

while True:

    wait_for_start()
    countdown()

    level = 1
    spin_speed = 0.12
    reaction_time = 2000

    print("Level 1 begins")
    print("Initial reaction time:", reaction_time)

    while True:

        check_pause()
        rainbow_spin(spin_speed)
        check_pause()

        color = random.choice(["yellow","blue","green","orange","cyan"])
        pos = random.randint(0, pixels-1)

        clear()

        if color == "yellow":
            np[pos] = (255,255,0)
            print("YELLOW shown - Use IR sensor")
        elif color == "blue":
            np[pos] = (0,0,255)
            print("BLUE shown - Use TOUCH sensor")
        elif color == "green":
            np[pos] = (0,255,0)
            print("GREEN shown - Use SHOCK sensor")
        elif color == "orange":
            np[pos] = (255,0,0)
            print("red shown - Do NOT react")
        else:
            np[pos] = (236,0,140)
            print("CYAN shown - Do NOT react")

        np.write()

        start = time.ticks_ms() #better than ms to measure reaction time
        correct = 0
        wrong = 0

        while time.ticks_diff(time.ticks_ms(), start) < reaction_time:

            check_pause()

            if color == "yellow" and ir.value() == 0:
                print("Correct IR detected")
                correct = 1
                break

            if color == "blue" and touch.value() == 1:
                print("Correct TOUCH detected")
                correct = 1
                break

            if color == "green" and shock.value() == 1:
                print("Correct SHOCK detected")
                correct = 1
                break

            if color == "yellow" and (touch.value() == 1 or shock.value() == 1):
                print("Wrong sensor used for YELLOW")
                wrong = 1
                break

            if color == "blue" and (ir.value() == 0 or shock.value() == 1):
                print("Wrong sensor used for BLUE")
                wrong = 1
                break

            if color == "green" and (ir.value() == 0 or touch.value() == 1):
                print("Wrong sensor used for GREEN")
                wrong = 1
                break

            if color in ["orange","cyan"] and (ir.value() == 0 or touch.value() == 1 or shock.value() == 1):
                print("Reacted to fake color")
                wrong = 1
                break

        clear()

        if wrong == 1:
            print("GAME OVER at Level", level)
            time.sleep(2)
            break

        if color in ["orange","cyan"]:
            print("Fake Color ignored")
            continue

        if correct == 1:
            print("Level", level, "completed")
            level += 1

            if spin_speed > 0.05:
                spin_speed -= 0.005

            if reaction_time > 600:
                reaction_time -= 150

            print("New Level:", level)
            print("New reaction time:", reaction_time)

            if level > 10:
                rainbow()
                break

        else:
            print("No reaction detected - Game Over")
            time.sleep(2)
            break