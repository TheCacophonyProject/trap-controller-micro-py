import pcf8563
import timezone
import datetime
from machine import I2C
from config import *

error_time_not_set = 3
error_no_program_found = 4

class Buzzer():
    def __init__():
        self.buzzer = Pin(5, Pin.OUT)
        self.off()

    def on(self):
        self.buzzer.high()

    def off(self):
        self.buzzer.low()

    def beep_trap_ready(self):
        for i in range(5):
            sleep(0.5)
            self.on()
            sleep(0.5)
            self.off()
        print("Trap is ready.")

    def beep_error(beeps, loop = True):
        while True:
            self.on()
            sleep(5)
            self.off()
            sleep(1)
            for i in range(beeps):
                self.on()
                sleep(0.1)
                self.off()
                sleep(0.1)
            sleep(1)
            if not loop:
                break

class Clock():
    def __init__(self):
        self.i2c = I2C(id=0, scl=Pin(config.I2C_SCL), sda=Pin(config.I2C_SDA))
        self.r = pcf8563.PCF8563(self.i2c)
        self.latitude = LATITUDE
        self.longitude = LONGITUDE
        dst = timezone.time_change_rule(-1, 6, 9, 2, 780)
        st = timezone.time_change_rule(0, 6, 4, 2, 720)        
        self.nz_tz = timezone.timezone(dst, st)
        self.always_on = Pin(PIN_24_7, Pin.IN, Pin.PULL_UP)

    def get_local_time(self, utc_time=None):
        if utc_time is None:
            utc_time = self.get_utc_time()
        return self.nz_tz.get_local_time(utc_time)

    def write_time(self, **kwargs):
        r.write_all(**kwargs)

    def get_utc_time(self):
        year, month, date, day, hour, minute, second = r.datetime()
        return datetime.datetime(year = year+2000, month = month, day = date, hour = hour, minute = minute, second = second)    

    def is_night():
        utc = self.get_utc_time()
        local_time = self.get_local_time(utc)
        tz = self.nz_tz.get_current_tz(utc).timezone
        sunrise = timezone.get_sunrise(utc, latitude, longitude, tz)
        sunset = timezone.get_sunset(utc, latitude, longitude, tz)
        return local_time.time() < sunrise or sunset < local_time.time()

    def in_active_window():
        return self.always_on.value() or self.is_night()

    def check_low_voltage():
        return r.check_low_voltage()

class Trap:
    def __init__(self):
        self.spool_power = Pin(config.spool_power, Pin.OUT)
        self.spool_power.low()
        
        self.spool1 = PWM(Pin(config.spool1))
        self.spool1.freq(50)

        self.spool2 = PWM(Pin(config.spool2))
        self.spool2.freq(50)

        self.pir1 = Pin(config.pir1)
        self.pir2 = Pin(config.pir2)

    def trigger_spools(self):
        print("Triggering spools")
        self.spool_power.high()
        self.spool1.duty_ns(servo_trigger)
        self.spool2.duty_ns(servo_trigger)
        sleep(0.5)
        self.spool1.duty_ns(servo_home)
        sleep(0.5)
        self.spool2.duty_ns(servo_home)
        sleep(1)
        spool_power.low()
  
    def reset_spool(spool):
        self.spool_power.high()
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
        self.spool_power.low()

    def reset_spools():
        print("Reset spool 1")
        self.reset_spool(self.spool1)
        print("Reset spool 2")
        self.reset_spool(self.spool2)
        print("Finished resetting spools, waiting 1 second.")
        sleep(1)

    def check_pirs(self):
        return self.pir1.value() or self.pir2.value()
