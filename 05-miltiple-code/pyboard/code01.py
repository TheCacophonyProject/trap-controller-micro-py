## Basic spool controller for trap PCB v0.2.0
import time
from time import sleep
from machine import I2C, Pin, PWM
import timezone
import datetime
import pcf8563

servo_home = 2150*1000
servo_reset = 500*1000
servo_trigger = 2450*1000

spool_power = Pin(13, Pin.OUT)
spool_power.low()

s1 = PWM(Pin(15))
s1.freq(50)
s2 = PWM(Pin(14))
s2.freq(50)

buzzer = Pin(5, Pin.OUT)
buzzer.low()

day_trigger = Pin(20, Pin.IN, Pin.PULL_UP)

pir1 = Pin(21)
pir2 = Pin(22)

i2c = I2C(id=0, scl=Pin(25), sda=Pin(24))
r = pcf8563.PCF8563(i2c)

latitude = -43.532055
longitude = 172.636230
dst = timezone.time_change_rule(-1, 6, 9, 2, 780)
st = timezone.time_change_rule(0, 6, 4, 2, 720)
nz_tz = timezone.timezone(dst, st)

#now = datetime.datetime(2022, 4, 3, 13, 1) # Now in UTC


def trigger_spools():
    print("Trigger spools")
    spool_power.high()
    s1.duty_ns(servo_trigger)
    s2.duty_ns(servo_trigger)
    sleep(1)
    s1.duty_ns(servo_home)
    s2.duty_ns(servo_home)
    sleep(1)
    spool_power.low()

def reset_spool(spool):
    spool_power.high()
    sleep(0.1)
    print("Reset")
    n = 5
    for i in range(n):
        angle = int(servo_home+(servo_reset-servo_home)*(i+1)/n)
        print(angle)
        spool.duty_ns(angle)
        sleep(1)
        spool.duty_ns(servo_home)
        sleep(1)
    
        
    spool.duty_ns(servo_reset)
    sleep(2.5)
    print("Home")
    spool.duty_ns(servo_home)
    sleep(2)
    spool_power.low()
        
def reset_spools():
    print("Reset spool 1")
    reset_spool(s1)
    print("Reset spool 2")
    reset_spool(s2)
    print("Finished resetting spool, waiting 1 second.")
    sleep(1)
    
def get_now():
    year, month, day, date, hour, minute, second = r.datetime()
    return datetime.datetime(year = year+2000, month = month, day = date, hour = hour, minute = minute, second = second)    

def is_night():
    utc = get_now()
    now = nz_tz.get_local_time(utc)
    sr = timezone.get_sunrise(utc, latitude, longitude, tz)
    ss = timezone.get_sunset(utc, latitude, longitude, tz)
    return now.time() < sr or ss < now.time() or not day_trigger.value()
    
reset_spools()

now = get_now()
tz = nz_tz.get_current_tz(now).timezone
print(now)

for i in range(5):
    sleep(0.5)
    buzzer.high()
    sleep(0.5)
    buzzer.low()

trap_active = True

while True:
    # Check if trap should be active
    night = is_night()
    if night and not trap_active:
        print("Making trap active as it's night")
        trap_active = True
    elif not night and trap_active:
        print("Making trap inactive as it is day")
        trap_active = False 
    

    if not trap_active:
        sleep(5)
        continue

    if (pir1.value() or pir2.value()):
        print("PIRs triggered")
        sleep(0.5)
        trigger_spools()
        sleep(60*10)
        reset_spools()
    sleep(0.1)