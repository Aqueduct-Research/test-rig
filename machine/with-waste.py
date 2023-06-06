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

pump_relay = Relay(13, 'pump')  # Relay connected to GPIO 13
input_relay = Relay(12, 'input')  # Relay connected to GPIO 12
waste_relay = Relay(14, 'waste')  # Relay connected to GPIO 14
switch = Switch(15)  # Switch connected to GPIO 15

waste_activated = False  # This flag will track whether the waste relay has been activated in the current cycle

while True:
    if switch.is_closed():
        pump_relay.on()
        input_relay.on()

        if not waste_activated:  # If the waste relay hasn't been activated in this cycle yet
            waste_relay.on()
            utime.sleep(5)  # Leave the waste relay on for 5 seconds
            waste_relay.off()
            waste_activated = True  # Mark the waste relay as activated for this cycle
    else:
        pump_relay.off()
        input_relay.off()
        waste_activated = False  # Reset the flag when the switch is opened, ready for the next cycle

    utime.sleep(0.1)  # To avoid debouncing issues
