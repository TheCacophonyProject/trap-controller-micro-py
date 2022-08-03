## Basic spool controller for trap PCB v0.2.0
import time
import timezone
import datetime
import pcf8563
from time import sleep
from machine import I2C, Pin, PWM

servo_home = 2250*1000
servo_reset = 550*1000
servo_trigger = 2450*1000


pir1 = Pin(18)
pir2 = Pin(19)

spool_power = Pin(11, Pin.OUT)
spool_power.low()

s1 = PWM(Pin(15))
s1.freq(50)
s2 = PWM(Pin(14))
s2.freq(50)

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
    print("Finished resetting spool, waiting 10 seconds.")
    sleep(10)
    
    
print("Starting test")

i2c = I2C(id=0, scl=Pin(25), sda=Pin(24))
r = pcf8563.PCF8563(i2c)
#r.write_all(seconds=0, minutes=24, hours=2, day=3, date=1, month=8, year=22)
year, month, day, date, hour, minute, second = r.datetime()
utc = datetime.datetime(year = year+2000, month = month, day = date, hour = hour, minute = minute, second = second)
print(utc)


print("======EXAMPLES======")
latitude = -43.532055
longitude = 172.636230
dst = timezone.time_change_rule(-1, 6, 9, 2, 780)
st = timezone.time_change_rule(0, 6, 4, 2, 720)
nz_tz = timezone.timezone(dst, st)
#now = datetime.datetime(2022, 4, 3, 13, 1) # Now in UTC
now = utc
print(now)

#print(_DAYS_BEFORE_MONTH)

print("UTC:    ", now)
tz = nz_tz.get_current_tz(now).timezone
print("TZ:     ", tz/60)
print("local:  ", nz_tz.get_local_time(now))
print("Sunrise:", timezone.get_sunrise(now, latitude, longitude, tz))
print("Sunset: ", timezone.get_sunset(now, latitude, longitude, tz))


while True:
    sleep(2)




reset_spools()
while True:        
    if (pir1.value() or pir2.value()):
        print("PIRs triggered")
        sleep(0.5)
        trigger_spools()
        sleep(60*10)
        reset_spools()
    sleep(0.1)
    




#utc
#print(local.time())
#print(sunrise)
#print(sunset)
#print(sunrise < local.time() and local.time() < sunset)