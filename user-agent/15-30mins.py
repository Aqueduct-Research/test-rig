import machine
import time
import uos
import urandom

RELAY_PIN = 13  # change this to the pin your relay is connected to
LOG_FILE = 'log.txt'  # change this to your preferred log file path

# initialize relay as output
relay = machine.Pin(RELAY_PIN, machine.Pin.OUT)

# initialize timer
timer = 0

# load previous total time if log file exists
try:
    with open(LOG_FILE, 'r') as f:
        timer = int(f.read())
except OSError:
    pass

# main loop
while True:
    # turn relay on
    relay.on()

    # start relay time
    relay_start_time = time.time()
    print('Relay on')

    # keep relay on for 15 seconds (abou5 1L of water)
    time.sleep(15)

    # turn relay off
    relay.off()
    print('Relay off')

    # update and print timer
    relay_end_time = time.time()
    relay_on_time = relay_end_time - relay_start_time
    timer += relay_on_time
    print('Total running time: {:.2f} seconds'.format(timer))

    # save total time to log file
    with open(LOG_FILE, 'w') as f:
        f.write(str(timer))

    # wait for a random time between 15 to 30 minutes
    wait_time = urandom.randint(15*60, 30*60)
    time.sleep(wait_time)

