from escpos.connections import getUSBPrinter


printer = getUSBPrinter()(idVendor=0x0483,
                          idProduct=0x070b,
                          inputEndPoint=0x81,
                          outputEndPoint=0x02) # Create the printer object with the connection params

# Print a image


printer.text("Hello World")
printer.lf()
