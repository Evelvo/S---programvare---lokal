from machine import Pin
r_led = Pin(15, Pin.OUT)
r_led.value(1)

from ssd1306 import SSD1306_I2C
from machine import PWM, I2C
i2c=I2C(0,sda=Pin(0), scl=Pin(1), freq=400000)
oled = SSD1306_I2C(128, 64, i2c)

g_led = Pin(14, Pin.OUT)
g_led.value(1)

b_led = Pin(7, Pin.OUT)
b_led.value(1)

def loading_screen():
    oled.fill(0)
    oled.text("loading...",1, 1)
    oled.show()

loading_screen()
    

import utime
import freesans20
import writer
import network
import framebuf
import urequests

wlan = network.WLAN(network.STA_IF)
wlan.active(True)


led = Pin("LED", Pin.OUT)


ned = Pin(5, Pin.IN, Pin.PULL_UP)
def ned1():
    return not ned.value()
venstre = Pin(4, Pin.IN, Pin.PULL_UP)
def venstre1():
    return not venstre.value()
enter = Pin(3, Pin.IN, Pin.PULL_UP)
def enter1():
    return not enter.value()
opp = Pin(6, Pin.IN, Pin.PULL_UP)
def opp1():
    return not opp.value()
hogre = Pin(2, Pin.IN, Pin.PULL_UP)
def hogre1():
    return not hogre.value()

oledbig = writer.Writer(oled, freesans20)

buzzer = PWM(Pin(11))


wlan.connect("SSID", "Passord")

sensor_temp = machine.ADC(4)
conversion_factor = 3.3 / (65535)

wifi = bytearray(b'\x00\x00\x00\x00\x00\x00\x00\xa8\x00\x07\xfe\x00\x1fW\x80x\x01\xe0\xe0\x00p\xc1\xf00\x07\xfe\x00\x0f\x0f\x00\x1c\x03\x80\x00`\x00\x01\xf8\x00\x03\xbc\x00\x00\x00\x00\x00@\x00\x00`\x00\x00 \x00\x00\x00\x00\x00\x00\x00')
no_wifi = bytearray(b'\x00\x00\x00\x00\x00\xc0\x00\xa8\xc0\x07\xff\x80\x1fW\x80x\x07\xe0\xe0\x0cp\xc1\xfc0\x07\xfe\x00\x0fo\x00\x1c\xc3\x80\x01\xe0\x00\x03\xf8\x00\x07\xbc\x00\r\x00\x00\x1a \x00\x18`\x000 \x00\x00\x00\x00\x00\x00\x00')

with open('log.txt', 'r') as reader:
    volum_log = reader.read()

volum = int(volum_log)
max_volum = 100000
min_volum = 0
volum_prosent = int((volum / 100000) * 100)
volume_pluses = [1000, 2000, 5000, 10000]
volume_pluses_amount = 4
volume_pluses_on = 0
volume_plus = 1000    


wlan = network.WLAN(network.STA_IF)
wlan.active(True)


def home_screen():
    oled.fill(0)
    reading = sensor_temp.read_u16() * conversion_factor 
    temperature = 27 - (reading - 0.706)/0.001721
    
    if wlan.isconnected():
        wifi1 = framebuf.FrameBuffer(wifi,20,20, framebuf.MONO_HLSB)
        oled.fill(0)
        oled.blit(wifi1,0,44)
    else:
        no_wifi1 = framebuf.FrameBuffer(no_wifi,20,20, framebuf.MONO_HLSB)
        oled.fill(0)
        oled.blit(no_wifi1,0,44)

    
    oledbig.set_textpos(45, 24)
    oledbig.printstring(f"{str(round(temperature))}*C")

    oled.text("Sindre",1, 1)
    oled.show()

def sound_screen():
    global volume_plus
    oled.fill(0)
    oled.text("Volume",1, 1)
    oled.text(str(volume_plus),1, 10)
    oledbig.set_textpos(45, 24)
    oledbig.printstring(f"{str(volum_prosent)}%")
    oled.text("-",24, 31)
    oled.text("+",104, 31)
    oled.show()

def test_screen():
    oled.fill(0)
    oled.text("Test",1, 1)
    oled.show()
    if wlan.isconnected():
        weather = urequests.get("http://192.168.128.224:5000/api").json()
        oled.text(weather["feels_temp"], 20, 20)
        oled.show()
    

    
    
home_screen()
g_led.value(0)

def playtone(frequency):
    global volum
    buzzer.duty_u16(volum)
    buzzer.freq(frequency)
    

def bequiet():
    buzzer.duty_u16(0)

def play_click():
    led.on()
    g_led.value(1)
    playtone(1500)
    utime.sleep(0.1)
    bequiet()
    led.off()
    g_led.value(0)

    
side_amount = 3
sides = ["home", "sound", "test"]
side_end = side_amount - 1
side = 0
on_side = "home"


def change_volume(up_down):
    global volume_plus
    global volum
    global max_volum
    global min_volum
    global volum_prosent
    if up_down == "plus":
        if volum < max_volum:
            volum = volum + volume_plus
            if volum > max_volum:
                volum = max_volum
        else:
            volum = max_volum
    elif up_down == "minus":
        if volum > min_volum:
            
            volum = volum - volume_plus
            if volum < min_volum:
                volum = min_volum
                
        else:
            return
    else:
        print("problemer med volum endrer")
    print(volum)
    volum_prosent = int((volum / max_volum) * 100)
    file = open("log.txt", "w")
    file.write(str(volum) + "\n")
    file.flush()
    sound_screen()

def change_volume_add():
    global volume_plus
    global volume_pluses
    global volume_pluses_on
    
    if volume_pluses_on < volume_pluses_amount - 1:

        volume_pluses_on = volume_pluses_on + 1
    else:
        volume_pluses_on = 0
    chosen = volume_pluses[volume_pluses_on]
    
    volume_plus = chosen
    
    sound_screen()
    
    

def load_side(up_down):
    global side
    global side_end
    global on_side
    if up_down == "opp":
        side = side - 1
    elif up_down == "ned":
        side = side + 1
    else:
        print("problemer med lasting av sider")
    print(side)
    if side < 0:
        side = 0
        playtone(100)
        utime.sleep(0.2)
        bequiet()
    elif side <= side_end:
        on_side = sides[side]
        print(on_side)
        play_click()
        if on_side == "home":
            home_screen()
        elif on_side == "sound":
            sound_screen()
        elif on_side == "test":
            test_screen()
            
            
    else:
        side = side_end
        playtone(100)
        utime.sleep(0.2)
        bequiet()
    
    
    

while True:
    utime.sleep(0.09)
    if ned1():
        load_side("ned")
    if venstre1():
        if on_side == "sound":
            change_volume("minus")
        else:
            print("venstre")
            play_click()
    if enter1():
        if on_side == "sound":
            change_volume_add()
        else:
            print("enter")
            play_click()
    if opp1():
        load_side("opp")
    if hogre1():
        if on_side == "sound":
            change_volume("plus")
        else:
            
            print("høgre")
            play_click()
        



    


