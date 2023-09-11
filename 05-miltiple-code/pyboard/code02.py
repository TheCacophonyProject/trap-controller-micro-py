## Basic spool controller for trap PCB v0.2.0
import time
from time import sleep
from machine import Pin, PWM
from config import servo_home, servo_reset, servo_trigger
from util import Trap, Buzzer

trigger = Pin(6)
trap = Trap()
buzzer = Buzzer()

trap.trigger_spools()
sleep(4)
trap.reset_spools()
buzzer.beep_trap_ready()

while True:        
    if (trigger.value()):
        print("triggered")
        trap.trigger_spools()
        sleep(60*10)
        trap.reset_spools()
    sleep(0.1)