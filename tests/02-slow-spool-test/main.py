## Basic spool controller for trap PCB v0.2.0
import time
from time import sleep
from machine import I2C, Pin, PWM

servo_home = 2200*1000
servo_reset = 500*1000
servo_trigger = 2450*1000

spool_power = Pin(13, Pin.OUT)
spool_power.low()

s1 = PWM(Pin(15))
s1.freq(50)
s2 = PWM(Pin(14))
s2.freq(50)


trigger = Pin(6)

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
    #for i in range(servo_home, servo_reset, -1000):
    #    spool.duty_ns(i)
    #    time.sleep(0.0018)
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
    
reset_spool(s1)
