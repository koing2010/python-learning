#
#  Mr.kon @2016/12/13
#
import binascii 
import struct


#password= (b'\x01\x09\x08\x09\x00\x06\x00\x04\x01\x09\x08\x09\x00\x06\x00\x04')
password = (b'\x37\x45\x42\x37\x30\x30\x39\x39\x30\x46\x45\x44\x30\x36\x31\x44')
#display hex string		
def HexShow(i_string):
	hex_string = ''
	hLen = len(i_string)
	for i in range(hLen):
		hvol = i_string[i]
		hhex = '%02X' % (hvol)
		hex_string += hhex + ' '
#	print('ReceiveBytes: %i_string' % (hex_string))
	print('lisence:',hex_string,'	total:',hLen)
	
#define  
def tea_encrypt(v,k):
#		v= bytes.fromhex(v)
#		print(v)
#		print('v: ')
#		HexShow(v)
#		print('k: ')
#		HexShow(k)
		y,z =  struct.unpack('<II',v)#+str.encode(v[1])+str.encode(v[2])+str.encode(v[3]))
#		print(y,z)
		sum_value= 0x00000000
		i = 0
		delta = 0x9e3779b9
		a,b,c,d =  struct.unpack('<IIII',k)#struct.unpack('I',str.encode(k[0])+str.encode(k[1])+str.encode(k[2])+str.encode(k[3]))

#		print("%d"%a,"%d"%b)
#	a = k[0] + k[1]<<8 + k[2]<< + k[3]

		for i in range(32):
			sum_value += delta
			sum_value &= 0xFFFFFFFF
			y += ((z << 4) + a) ^ (z + sum_value) ^ ((z >> 5) + b)
			y &= 0xFFFFFFFF
			z += ((y << 4) + c) ^ (y + sum_value) ^ ((y >> 5) + d)
			z &= 0xFFFFFFFF
#			print(y,z)
#		print(y,z)
		r = struct.pack('<II',y,z)
		return r
		
#**********************************************************************************************
def encrypt(src,size_src,key):

	a = 0
	i = 0
	num = 0

	#将明文补足为8字节的倍数
	a = size_src % 8
	if a != 0:
		for i in range(8 - a):		
			src[size_src] = 0x00
			size_src += 1
	#加密
	num = size_src / 8
	s = (b'')
	for i in range(int(num)):
		#string = stmp(src
		s += tea_encrypt(src[i*8:i*8+8],key)
#	HexShow(s)
#	HexShow(tea_encrypt(s[0:8],key))
	return s

#*********************************

#******************************************************************************


InputMac=input('Input MAC eg:00 12 4B 00 07 6B 03 44"')
MySalt = (b'\x0A\x0B\x0C\x0D\x0E\x0F\x1A\xAB')
if len(InputMac) is 23:
	print('success')
	BufAddSalt = bytes.fromhex(InputMac)#+ MySalt
#输入的顺序倒换一下
	x,y = struct.unpack('<LL',BufAddSalt)
	BufAddSalt =  struct.pack('>LL',y,x)
#	print(len(BufAddSalt))
#	print(BufAddSalt)
#	HexShow(BufAddSalt)
#	BufAddSalt = tea_encrypt(InputMac,password)
#	print(BufAddSalt )
#加密两侧
	FirstBytes = encrypt(BufAddSalt,len(BufAddSalt),password)
	TargetBytes = encrypt(FirstBytes[0:8],8,password)
#结果输出也倒换一下
	x,y = struct.unpack('<LL',TargetBytes)
	TargetBytes =  struct.pack('>LL',y,x)
	HexShow(TargetBytes)
else:
	print('lenth erro')
input('Ctrl+A copy the lisence, and press enter exit')
