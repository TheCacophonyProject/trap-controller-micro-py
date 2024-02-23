## Basic spool controller for trap PCB v0.2.0
from time import sleep
from machine import Pin
from util import Trap, Clock, Buzzer

trap = Trap()
buzzer = Buzzer()

while True:
    pir1 = trap.pir1.value()
    pir2 = trap.pir2.value()
    if pir1 and pir2:
        buzzer.on()
    elif pir1:
        buzzer.pwm(400, 50)
    elif pir2:
        buzzer.pwm(1000, 50)
    else:
        buzzer.off()
    sleep(0.1)
