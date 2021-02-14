import machine
import sys
import utime
import xbee

# Pin definitions
repl_button = machine.Pin(machine.Pin.board.D5, machine.Pin.IN, machine.Pin.PULL_UP)
led = machine.Pin(machine.Pin.board.D4, machine.Pin.OUT)

x = xbee.XBee()
test_data = 'Hello World!'

# Wait for button 5 to be pressed, and then exit
while True:
    # if button 5 is pressed, drop to repl_button
    if  repl_button.value() == 0:
        #print("Dropping to REPL")

        print("Transmitting to Coordinator")
        print("Source Address: %s" % x.atcmd('MY'))
        xbee.transmit(xbee.ADDR_COORDINATOR, test_data)

        #sys.exit()


    # turn LED on and off
    led.value(1)
    utime.sleep_ms(500)
    led.value(0)
    utime.sleep_ms(500)
