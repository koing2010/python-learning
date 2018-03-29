#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
"""
Handling raw data inputs example
"""
from time import sleep
from msvcrt import kbhit

import pywinusb.hid as hid

class UserDevice:
    vendor_id = 0x07da
    product_id = 0x2010

def sample_handler(data):
    #print("Rxdata",data)
    if(data[1] == 0x85):
        if data[3] == 0xa5:
            print("CHIP = CC2530 " , "CHIP_REV = %02X\n" % data[4])
        elif data[3] == 0xb5:
            print("CHIP = CC2531 ", "CHIP_REV = %02X\n" % data[4])
        elif data[3] == 0x95:
            print("CHIP = CC2533 ", "CHIP_REV = %02X\n" % data[4])
        elif data[3] == 0x8d:
            print("CHIP = CC2540 ", "CHIP_REV = %02X\n" % data[4])
        elif data[3] == 0x41:
            print("CHIP = CC2541 ", "CHIP_REV = %02X\n" % data[4])
        else:
            print("CHIP not Found!\n ")
    else:
        print("Raw data: 0X{0}".format(data))
def sample_write(device, send_list):
    report = device.find_output_reports()
   # print(report)
    if report:
        report[0].set_raw_data(send_list)
        bytes_num = report[0].send()
    return bytes_num
def raw_test():
    # simple test
    # browse devices...
    all_hids = hid.find_all_hid_devices()
    if all_hids:
        while True:
            print("Choose a device to monitor raw input reports:\n")
            print("0 => Exit")
            for index, device in enumerate(all_hids):
                device_name = unicode("{0.vendor_name} {0.product_name}" \
                        "(vID=0x{1:04x}, pID=0x{2:04x})"\
                        "".format(device, device.vendor_id, device.product_id))
                print("{0} => {1}".format(index+1, device_name))
                if(device.vendor_id == UserDevice.vendor_id) and (device.product_id == UserDevice.product_id):
                    break

            # print("\n\tDevice ('0' to '%d', '0' to exit?) " \
            #        "[press enter after number]:" % len(all_hids))
            #index_option = raw_input()
            #if index_option.isdigit() and int(index_option) <= len(all_hids):
                # invalid
             #   break;
        #int_option = int(index_option)
        #if int_option:
            #device = all_hids[int_option-1]
            try:
                device.open()

                #set custom raw data handler
                device.set_raw_data_handler(sample_handler)

                print("\nWaiting for data...\nPress any (system keyboard) key to stop...")
                while not kbhit() and device.is_plugged():
                    #just keep the device opened to receive events
                    sleep(3)
                    send_list = [0x00 for i in range(9)]
                    for i in range(9):
                        send_list[i] = i+10
                    send_list[0] = 0x00
                    send_list[1] = 0x03
                    sample_write(device, send_list)
                return
            finally:
                device.close()
    else:
        print("There's not any non system HID class device available")
#
if __name__ == '__main__':
    # first be kind with local encodings
    import sys
    if sys.version_info >= (3,):
        # as is, don't handle unicodes
        unicode = str
        raw_input = input
    else:
        # allow to show encoded strings
        import codecs
        sys.stdout = codecs.getwriter('mbcs')(sys.stdout)
    raw_test()

