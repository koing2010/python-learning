#
#  Mr.kon @2016/12/13
#
import binascii 


password= (b'\x01\x09\x08\x09\x00\x06\x00\x04\x01\x09\x08\x09\x00\x06\x00\x04')
#define  
def tea_encrypt(v,k):
	y = v[0] 
	z = v[1] 
	sum_value= 0 
	i
	delta = 0x9e3779b9
	a = k[0] 
	b = k[1] 
	c = k[2] 
	d = k[3]
    for i in range(32):
		sum_value += delta
		y += ((z << 4) + a) ^ (z + sum_value) ^ ((z >> 5) + b)
		z += ((y << 4) + c) ^ (y + sum_value) ^ ((y >> 5) + d)
	v[0] = y
	v[1] = z
#******************************************************************************


InputMac=input('Input MAC eg:01 02 03 04 05 06 07 08"')
MySalt = (b'\x5A\xA5\x10\x01\x01\x00\x00\x00\x02\x02\x01\xA5\x5A')
if len(InputMac) is 23:
	print('success')
	BufAddSalt = bytes.fromhex(InputMac)+ MySalt
	print(BufAddSalt)
else:
	print('lenth erro')
input('press enter exit')
