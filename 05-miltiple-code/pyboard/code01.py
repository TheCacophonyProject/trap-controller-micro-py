## Basic spool controller for trap PCB v0.2.0
from time import sleep
from machine import Pin
from util import Trap, Clock, Buzzer

trap = Trap()
clock = Clock()
buzzer = Buzzer()

trap.trigger_spools()
sleep(4)
trap.reset_spools()
buzzer.beep_trap_ready()

if clock.in_active_window():
    trap_active = True
    print("Trap is active")
else:
    trap_active = False
    print("Trap is inactive")

while True:
    in_active_window = clock.in_active_window()
    if in_active_window != trap_active:
        if in_active_window:
            print("Making trap active")
        else:
            print("Making trap inactive")
        trap_active = in_active_window

    if not trap_active:
        sleep(1)
        continue

    if (trap.check_pirs()):
        print("PIRs triggered")
        sleep(0.5)
        trap.trigger_spools()
        sleep(60*10)
        trap.reset_spools()
    sleep(0.1)