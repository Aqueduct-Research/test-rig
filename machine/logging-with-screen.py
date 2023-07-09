from machine import Pin, I2C
import utime
import uos
import ssd1306

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
        return self.cumulative_time / 60000  # convert milliseconds to minutes

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
                relay.cumulative_time = float(lines[i+1].strip()) * 60000  # convert minutes to milliseconds
            return cycles
    except:
        return 0

def save_data(relays, cycles):
    with open('relay_data.txt', 'w') as f:
        f.write(f"Cycles: {cycles}\n")
        for relay in relays:
            f.write(f"{relay.name}: {relay.get_cumulative_time():.2f}m\n")

class Display:
    def __init__(self, width, height, scl, sda):
        self.i2c = I2C(0, scl=Pin(scl), sda=Pin(sda), freq=400000)
        self.display = ssd1306.SSD1306_I2C(width, height, self.i2c)

    def write(self, lines):
        self.display.fill(0)  # Clear the display
        for i, line in enumerate(lines):
            self.display.text(line, 0, i*16)
        self.display.show()  # Update the display

pump_relay = Relay(13, 'pump')  # Relay connected to GPIO 13
input_relay = Relay(12, 'input')  # Relay connected to GPIO 12
waste_relay = Relay(14, 'waste')  # Relay connected to GPIO 14
switch = Switch(15)  # Switch connected to GPIO 15

relays = [pump_relay, input_relay, waste_relay]
cycle_count = load_data(relays)

was_open = switch.is_closed()

oled = Display(128, 64, 22, 21)  # 128x64 OLED display connected to GPIO 22 (SCL) and 21 (SDA)

while True:
    if switch.is_closed():
        if pump_relay.start_time is None:
            pump_relay.on()
        if input_relay.start_time is None:
            input_relay.on()
        if was_open:
            waste_relay.on()
            utime.sleep(5)
            waste_relay.off()
        was_open = False
    else:
        if pump_relay.start_time is not None:
            pump_relay.off()
        if input_relay.start_time is not None:
            input_relay.off()
        if waste_relay.start_time is not None:
            waste_relay.off()
        if not was_open:
            cycle_count += 1
            save_data(relays, cycle_count)
        was_open = True
    oled.write([
        "Cycles: " + str(cycle_count),
        "Pump: {:.2f}m".format(pump_relay.get_cumulative_time()),
        "Input: {:.2f}m".format(input_relay.get_cumulative_time()),
        "Waste: {:.2f}m".format(waste_relay.get_cumulative_time())
    ])
    utime.sleep(3)

