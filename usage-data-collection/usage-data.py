from machine import Pin
import time

FLOW_SENSOR_PIN = 14  # Update this to the pin your flow sensor data line is connected to

# This will be triggered each time the flow sensor sees a flow
def pulse_callback(p):
    global pulse_count
    pulse_count += 1

pulse_count = 0
flow_sensor = Pin(FLOW_SENSOR_PIN, Pin.IN)
flow_sensor.irq(trigger=Pin.IRQ_RISING, handler=pulse_callback)

while True:
    time.sleep(1)  # wait for 1 second
    print('Flow rate: ', pulse_count, 'pulses per second')
    pulse_count = 0  # reset the pulse count
