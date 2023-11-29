## Basic spool controller for trap PCB v0.2.0
import time
from time import sleep
from machine import I2C, Pin, PWM
from util import Trap

trap = Trap()

while True:
    trap.trigger_spools()
    sleep(10)
    trap.reset_spools()
    sleep(70)
