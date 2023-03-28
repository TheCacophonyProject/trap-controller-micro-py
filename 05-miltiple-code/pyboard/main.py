from machine import Pin, I2C
from time import sleep
import pcf8563
import os
import datetime

rc1 = Pin(16, Pin.IN, Pin.PULL_UP)
rc2 = Pin(18, Pin.IN, Pin.PULL_UP)
rc4 = Pin(17, Pin.IN, Pin.PULL_UP)
rc8 = Pin(19, Pin.IN, Pin.PULL_UP)
buzzer = Pin(5, Pin.OUT)
buzzer.value(0)

uploadtimeFile = "uploadtime.py"

try:
    os.stat(uploadtimeFile)
    first_run = True
except OSError:
    first_run = False

i2c = I2C(id=0, scl=Pin(25), sda=Pin(24))
r = pcf8563.PCF8563(i2c)

if first_run:
    import uploadtime
    r.write_all(seconds=uploadtime.seconds, minutes=uploadtime.minutes, hours=uploadtime.hours, day=uploadtime.day_of_week, date=uploadtime.date, month=uploadtime.month, year=uploadtime.year)
    os.remove(uploadtimeFile)
    print("updated the RTC time.")

if r.check_low_voltage() != 0:
    while True:
        buzzer(1)
        sleep(5)
        buzzer(0)
        sleep(1)
        for i in range(3):
            buzzer(1)
            sleep(0.1)
            buzzer(0)
            sleep(0.1)
        sleep(1)

year, month, date, day, hour, minute, second = r.datetime()
print("rtc time is (UTC)")
print(datetime.datetime(year = year+2000, month = month, day = date, hour = hour, minute = minute, second = second))



n = 15 - rc1.value() - 2*rc2.value() - 4*rc4.value() - 8*rc8.value()

sleep(1)
for i in range(3):
    buzzer(1)
    sleep(0.1)
    buzzer(0)
    sleep(0.1)
sleep(1)
for i in range(n):
    buzzer(1)
    sleep(0.2)
    buzzer(0)
    sleep(0.2)
sleep(1)
for i in range(3):
    buzzer(1)
    sleep(0.1)
    buzzer(0)
    sleep(0.1)
sleep(1)

if n == 1:
    print("running code01.py")
    exec(open('/code01.py').read())
elif n == 2:
    print("running code02.py")
    exec(open('/code02.py').read())
else:
    print("no code to run")
    