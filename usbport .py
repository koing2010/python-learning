import time
import threading
import usb.core
import usb.util
import sys
#define the PID & VID
idVendor = 0x0483
idProduct = 0x7540
dev =  usb.core.find(idVendor, idProduct)
cfg = dev.get_active_configuration()
intf = cfg[(0,0)]
ep = usb.util.find_descriptor(
	intf,
	# match the first OUT endpoint
	custom_match = \
	lambda e: \
		usb.util.endpoint_direction(e.bEndpointAddress) == \
		usb.util.ENDPOINT_OUT
)
print 'The length of data(write USB) is:', ep.write('WANTFORGETTXT')
ep_read = usb.util.find_descriptor(
	intf,
	# match the first IN endpoint
	custom_match = \
	lambda e: \
		usb.util.endpoint_direction(e.bEndpointAddress) == \
		usb.util.ENDPOINT_IN
)
data_len = ep_read.read(4)
print 'Get USB data:',data_len
len = (data_len[3] << 24) + (data_len[2] << 16) + (data_len[1] << 8) + data_len[0]
print 'data len is:',len
dev.reset()
