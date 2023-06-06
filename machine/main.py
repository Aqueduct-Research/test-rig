from machine import Pin
import utime

class Relay:
    def __init__(self, pin, name):
        self.relay = Pin(pin, Pin.OUT)
        self.name = name

    def on(self):
        self.relay.value(1)
        print(f'{self.name} relay turned on')

    def off(self):
        self.relay.value(0)
        print(f'{self.name} relay turned off')

class Switch:
    def __init__(self, pin):
        self.switch = Pin(pin, Pin.IN, Pin.PULL_UP)

    def is_closed(self):
        return self.switch.value() == 0

pump_relay = Relay(13, 'pump')  # Relay connected to GPIO 2
input_relay = Relay(12, 'input')  # Relay connected to GPIO 3
switch = Switch(15)  # Switch connected to GPIO 4

while True:
    if switch.is_closed():
        pump_relay.on()
        input_relay.on()
    else:
        pump_relay.off()
        input_relay.off()

    utime.sleep(0.1)  # To avoid debouncing issues
