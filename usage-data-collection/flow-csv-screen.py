from machine import Pin, Timer, I2C
import time
import ssd1306  # SSD1306 is the OLED driver. Make sure it's available on your device.

FLOW_SENSOR_PIN = 14  # Update this to the pin your flow sensor data line is connected to
FLOW_TIMEOUT = 3  # time in seconds to consider the flow as continuous
FLOW_THRESHOLD = 50  # Only consider flow "on" if pulse count in the last second is above this value
CONVERSION_FACTOR = 38  # Conversion factor from pulses per second to liters per minute
FILENAME = 'flow_data.csv'  # name of the file to write to

flow_detected = False
pulse_count = 0
start_time = 0
cumulative_volume = 0
above_threshold_time = 0

i2c = I2C(scl=Pin(4), sda=Pin(5))  # Modify these pin numbers to match your setup
display = ssd1306.SSD1306_I2C(128, 64, i2c)

# This will be triggered each time the flow sensor sees a flow
def pulse_callback(p):
    global pulse_count
    pulse_count += 1

def check_flow(t):
    global pulse_count, flow_detected, start_time, cumulative_volume, above_threshold_time
    flow_rate = round(pulse_count / CONVERSION_FACTOR, 4)  # Conversion from pulses/sec to liters/min
    if pulse_count > FLOW_THRESHOLD:
        if not flow_detected:
            above_threshold_time += 1
            if above_threshold_time >= FLOW_TIMEOUT:
                flow_detected = True
                start_time = time.time()
                above_threshold_time = 0
    else:
        above_threshold_time = 0
        flow_off()
    cumulative_volume += flow_rate * (1 / 60)  # Add the volume since last check
    pulse_count = 0
    flow_status = 'Flow: ON' if flow_detected else 'Flow: OFF'
    timestamp = 'Time: ' + str(time.time())
    lpm = 'L/m: ' + str(flow_rate)
    print(timestamp)
    print(flow_status)
    print(lpm)
    display.fill(0)  # Clear the display
    display.text(timestamp, 0, 0)  # Write the time on the display
    display.text(flow_status, 0, 24)  # Write the flow status on the display
    display.text(lpm, 0, 36)  # Write the flow rate on the display
    display.show()  # Update the display to show the new text

def flow_off():
    global flow_detected, start_time, cumulative_volume
    if flow_detected:
        flow_detected = False
        duration = time.time() - start_time
        with open(FILENAME, 'a') as f:
            f.write(f"{start_time}, {duration}, {cumulative_volume}\n")

flow_sensor = Pin(FLOW_SENSOR_PIN, Pin.IN)
flow_sensor.irq(trigger=Pin.IRQ_RISING, handler=pulse_callback)
flow_check_timer = Timer(1)
flow_check_timer.init(period=1000, mode=Timer.PERIODIC, callback=check_flow)

while True:
    time.sleep(1)  # wait for 1 second

