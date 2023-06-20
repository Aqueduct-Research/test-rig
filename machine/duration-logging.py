from machine import Pin
import utime
import uos

class Relay:
    def __init__(self, pin, name):
        self.relay = Pin(pin, Pin.OUT)
        self.name = name
        self.start_time = None
        self.cumulative_time = 0

    def on(self):
        self.relay.value(1)
        self.start_time = utime.ticks_ms()

    def off(self):
        self.relay.value(0)
        if self.start_time is not None:
            self.cumulative_time += utime.ticks_diff(utime.ticks_ms(), self.start_time)
            self.start_time = None

    def get_cumulative_time(self):
        return self.cumulative_time / 1000  # convert milliseconds to seconds

class Switch:
    def __init__(self, pin):
        self.switch = Pin(pin, Pin.IN, Pin.PULL_UP)

    def is_closed(self):
        return self.switch.value() == 0

def load_data(relays):
    try:
        with open('relay_data.txt', 'r') as f:
            lines = f.readlines()
            cycles = int(lines[0].strip())
            for i, relay in enumerate(relays):
                relay.cumulative_time = float(lines[i+1].strip()) * 1000  # convert seconds to milliseconds
            return cycles
    except:
        return 0

def save_data(relays, cycles):
    with open('relay_data.txt', 'w') as f:
        f.write(f"{cycles}\n")
        for relay in relays:
            f.write(f"{relay.get_cumulative_time()}\n")

def log_to_file(file_name, relays, cycles):
    with open(file_name, 'w') as f:
        for relay in relays:
            f.write(f"{relay.name} relay cumulative active time: {relay.get_cumulative_time()} seconds\n")
        f.write(f"Total cycles: {cycles}\n")

pump_relay = Relay(13, 'pump')  # Relay connected to GPIO 13
input_relay = Relay(12, 'input')  # Relay connected to GPIO 12
waste_relay = Relay(14, 'waste')  # Relay connected to GPIO 14
switch = Switch(15)  # Switch connected to GPIO 15

relays = [pump_relay, input_relay, waste_relay]
cycle_count = load_data(relays)
waste_activated = False

while True:
    if switch.is_closed():
        if pump_relay.start_time is None:
            pump_relay.on()
        if input_relay.start_time is None:
            input_relay.on()
        if not waste_activated:
            waste_relay.on()
            utime.sleep(5)
            waste_relay.off()
            waste_activated = True
    else:
        if pump_relay.start_time is not None:
            pump_relay.off()
        if input_relay.start_time is not None:
            input_relay.off()
        if waste_relay.start_time is not None:
            waste_relay.off()
        waste_activated = False
        cycle_count += 1
        save_data(relays, cycle_count)
    utime.sleep(3)
