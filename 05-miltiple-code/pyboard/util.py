import pcf8563
import timezone
import datetime
from machine import I2C, UART, Pin, PWM
from config import *
from time import sleep

class Buzzer():
    def __init__(self):
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

    def beep_error(self, beeps, loop = True):
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
        self.i2c = I2C(id=0, scl=Pin(PIN_SCL), sda=Pin(PIN_SDA))
        self.r = pcf8563.PCF8563(self.i2c)
        self.latitude = LATITUDE
        self.longitude = LONGITUDE
        dst = timezone.time_change_rule(-1, 6, 9, 2, 780)
        st = timezone.time_change_rule(0, 6, 4, 2, 720)        
        self.nz_tz = timezone.timezone(dst, st)
        self.night_only = Pin(PIN_24_7, Pin.IN, Pin.PULL_UP)

    def get_local_time(self, utc_time=None):
        if utc_time is None:
            utc_time = self.get_utc_time()
        return self.nz_tz.get_local_time(utc_time)

    def write_time(self, **kwargs):
        self.r.write_all(**kwargs)

    def get_utc_time(self):
        year, month, date, day, hour, minute, second = self.r.datetime()
        return datetime.datetime(year = year+2000, month = month, day = date, hour = hour, minute = minute, second = second)    

    def is_night(self):
        utc = self.get_utc_time()
        local_time = self.get_local_time(utc)
        tz = self.nz_tz.get_current_tz(utc).timezone
        sunrise = timezone.get_sunrise(utc, LATITUDE, LONGITUDE, tz)
        sunset = timezone.get_sunset(utc, LATITUDE, LONGITUDE, tz)
        return local_time.time() < sunrise or sunset < local_time.time()

    def in_active_window(self):
        return (not self.night_only.value()) or self.is_night()

    def check_low_voltage(self):
        return self.r.check_low_voltage()

class RP_UART():
    def __init__(self):
        self.uart = UART(0, baudrate=9600, tx=Pin(PIN_UART_TX), rx=Pin(PIN_UART_RX))
    
    def read_line_from_uart(self):
        line = bytearray()
        while True:
            if self.uart.any():
                char = self.uart.read(1)
                if char == b'\n':
                    break
                line.extend(char)
        return line

    def wait_for_line(self, line):
        while True:
            if bytearray(line) == self.read_line_from_uart():
                break

class Trap:
    def __init__(self):
        self.spool_power = Pin(PIN_SPOOL_POWER, Pin.OUT)
        self.spool_power.low()
        
        self.spool1 = PWM(Pin(PIN_SPOOL_1))
        self.spool1.freq(50)

        self.spool2 = PWM(Pin(PIN_SPOOL_2))
        self.spool2.freq(50)

        self.pir1 = Pin(PIN_PIR_1, Pin.IN)
        self.pir2 = Pin(PIN_PIR_2, Pin.IN)

        self.led = Pin(PIN_LED, Pin.OUT)

        self.state = None

    def trigger_spools(self):
        self.state = "triggering"
        print("Triggering spools")
        self.spool_power.high()
        self.spool1.duty_ns(SERVO_TRIGGER)
        self.spool2.duty_ns(SERVO_TRIGGER)
        sleep(0.5)
        self.spool1.duty_ns(SERVO_HOME)
        sleep(0.5)
        self.spool2.duty_ns(SERVO_HOME)
        sleep(1)
        self.spool_power.low()
        self.state = "triggered"
  
    def reset_spool(self, spool):
        self.state = "resetting"
        self.spool_power.high()
        sleep(0.1)
        print("Reset")
        n = 5
        for i in range(n):
            angle = int(SERVO_HOME+(SERVO_RESET-SERVO_HOME)*(i+1)/n)
            print(angle)
            spool.duty_ns(angle)
            sleep(2)
            spool.duty_ns(SERVO_HOME)
            sleep(2)    
        spool.duty_ns(SERVO_RESET)
        sleep(2.5)
        print("Home")
        spool.duty_ns(SERVO_HOME)
        sleep(2)
        self.spool_power.low()
        self.state = "reset"

    def reset_spools(self):
        print("Reset spool 1")
        self.reset_spool(self.spool1)
        print("Reset spool 2")
        self.reset_spool(self.spool2)
        print("Finished resetting spools, waiting 1 second.")
        sleep(1)

    def check_pirs(self):
        #print(self.pir1.value())
        #print(self.pir2.value())
        return self.pir1.value() or self.pir2.value()

    def write_led(self, on):
        self.led.value(on)