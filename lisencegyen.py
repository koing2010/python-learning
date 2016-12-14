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
def tea_decrypt(v,k):
	y = v[0]
	z = v[1]
	sum = 0xC6EF3720
	i
	delta = 0x9e3779b9
	a = k[0]
	b = k[1]
	c = k[2]
	d = k[3]
	for i in range(32):
		z -= ((y << 4) + c) ^ (y + sum) ^ ((y >> 5) + d)
		y -= ((z << 4) + a) ^ (z + sum) ^ ((z >> 5) + b)
		sum -= delta
	v[0] = y
	v[1] = z
#*****************************************************************************
#加密
def encrypt(src, size_src, key):
	a = 0
	i = 0
	num = 0
#将明文补足为8字节的倍数
	a = size_src % 8
	if a != 0:
		for i in range(8 - a):
			src[size_src] = 0
			size_src = size_src + 1
#加密
	num = int(size_src/8)
	for i in range(num):
		tea_encrypt(src + i * 8 ,key)
	return size_src

#***************************************************************************
#解密
def decrypt(src, size_src, key):
	i = 0
	num = 0
	#判断长度是否为8的倍数
	if (size_src % 8) != 0:
		return 0
	#解密
	num = size_src / 8
	for i in range(num):
		tea_decrypt((src + i * 8), key)
	return size_src
#***************************************************************************
InputMac=input('Input MAC eg:01 02 03 04 05 06 07 08"')
MySalt = (b'\x0a\x0b\x0c\x0d\x0e\x0f\x1a\xab')
if len(InputMac) is 23:
	print('success')
	BufAddSalt = bytes.fromhex(InputMac)+ MySalt
	encrypt(BufAddSalt, len(BufAddSalt), password)
	print(BufAddSalt)
else:
	print('lenth erro')
input('press enter exit')
