from machine import Pin, Timer
import time

# detects flow with threshold each second, prints flow on or off as well as Liters per minute flow rate. Any output below the threshold where flow=0 should be ignored.

FLOW_SENSOR_PIN = 14  # Update this to the pin your flow sensor data line is connected to
FLOW_TIMEOUT = 1  # time in seconds without flow to consider the flow as off
FLOW_THRESHOLD = 10  # Only consider flow "on" if pulse count in the last second is above this value
CONVERSION_FACTOR = 38  # Conversion factor from pulses per second to liters per minute

flow_detected = False
pulse_count = 0

# This will be triggered each time the flow sensor sees a flow
def pulse_callback(p):
    global pulse_count
    pulse_count += 1

def check_flow(t):
    global pulse_count, flow_detected, timer
    flow_rate = round(pulse_count / CONVERSION_FACTOR, 4)  # Conversion from pulses/sec to liters/min
    if pulse_count > FLOW_THRESHOLD:
        flow_detected = True
        timer.init(period=FLOW_TIMEOUT * 1000, mode=Timer.ONE_SHOT, callback=flow_off)
    pulse_count = 0
    print(f"{int(flow_detected)}, {flow_rate}")

def flow_off(t):
    global flow_detected
    flow_detected = False

flow_sensor = Pin(FLOW_SENSOR_PIN, Pin.IN)
flow_sensor.irq(trigger=Pin.IRQ_RISING, handler=pulse_callback)
timer = Timer(0)
flow_check_timer = Timer(1)
flow_check_timer.init(period=1000, mode=Timer.PERIODIC, callback=check_flow)

while True:
    time.sleep(1)  # wait for 1 second
