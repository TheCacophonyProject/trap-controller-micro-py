# The Cacophony Project Trap Controller v0.1
# This trap controller is programmed to work in several different configurations.
#
# Single board; Spool: 
#       1) Only at night, trigger spools 1 second after PIRs are triggered.
#       2) Reset spools after 10 minutes
#
# Double board; Spool and Cage:
#       Board A)
#           1) When first powered on reset spools.
#           2) Only at night, trigger spools 1 second after the PIR is triggered.
#           3) Notify Board B through modbus that trap has been triggered.
#           4) Reset spools after 10 minutes.
#       Board B)
#           1) When first powered on reset ratchet door.
#           2) Wait for Board A to notify that spools have been triggered. 
#           3) Wait a few seconds, then when PIR is triggered, close ratchet door.
#           4) Reset ratchet door when?       
#
# Triple board; Spool, Cage, and Killing.
#       Board A)
#           1) When first powered on reset spools.
#           2) Only at night, trigger spools 1 second after PIRs are triggered.
#           3) Notify Board B through modbus that trap has been triggered.
#           4) Reset spools after 10 minutes.
#       Board B)
#           1) When first powered on reset ratchet door.
#           2) Wait for Board A to notify that spools have been triggered. 
#           3) Wait a few seconds, then when PIR is triggered, close ratchet door.
#       Board C)
#           1) Killing mechanism is unknown so far.
#
# IR camera and Spool:
#       IR Camera
#           1) Poll PIR on Spool controller to detect movement.
#           2) Turn on IR camera when there is movement.
#           3) Trigger spools when ready.
#       Spool Board)
#           1) Listen on modbus for instructions/actions from IR camera
#

#import utime
import time
from time import sleep
from machine import I2C, Pin, PWM

servo_home = 2250*1000
servo_reset = 550*1000
servo_trigger = 2450*1000


pir1 = Pin(18)
pir2 = Pin(19)
pir3 = Pin(20)
pir4 = Pin(21)

spool_power = Pin(29, Pin.OUT)
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

reset_spools()
while True:        
    if (pir1.value() or pir2.value() or pir3.value() or pir4.value()):
        print("PIRs triggered")
        sleep(1)
        trigger_spools()
        sleep(60*10)
        reset_spools()
        
    sleep(0.1)
    


#utc
#print(local.time())
#print(sunrise)
#print(sunset)
#print(sunrise < local.time() and local.time() < sunset)