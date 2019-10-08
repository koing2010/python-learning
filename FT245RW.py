# ----------
# import the PyUSB module
import ftd2xx

# list devices by description, returns tuple of attached devices description strings
d = ftd2xx.listDevices(ftd2xx.OPEN_BY_DESCRIPTION)
print(d)

# list devices by serial, returns tuple of attached devices serial strings
d = ftd2xx.listDevices() # implicit d2xx.OPEN_BY_SERIAL_NUMBER
print(d)

h = ftd2xx.open(0)
print(h)

# read eeprom
print( h.eeRead() )

# get queue status
print( h.getQueueStatus())

# set RX/TX timeouts
h.setTimeouts(1000,1000)

# write bytes (serial mode)
print(  h.write('Hello world!') )

# read bytes (serial mode)
print( h.read(5))

#close port
h.close()
# ----------
