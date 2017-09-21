import struct
from ctypes import *

def encipher(v, key):
    y=c_int32( struct.unpack('<i', v[0:4])[0])
    z=c_int32( struct.unpack('<i', v[4:])[0])
    k = struct.unpack('<iiii',key)
    print("yz value:",hex(y.value),hex(z.value))
    sum=c_int32(0)
    delta=0x9E3779B9
    n=32
    w=[0,0]

    while(n > 0):
        sum.value += delta
        y.value += (( z.value << 4 ) + k[0]) ^ (z.value + sum.value) ^ (( z.value >> 5 ) + k[1])
        z.value += (( y.value << 4 ) + k[2]) ^ (y.value + sum.value) ^ (( y.value >> 5 ) + k[3])
        n -= 1

    w[0]=y.value
    w[1]=z.value
    r = struct.pack('<ii',w[0],w[1])
    return r


def tea_encrypt(v, k):
    y=c_int32( struct.unpack('<i', v[0:4])[0])
    z=c_int32( struct.unpack('<i', v[4:])[0])
   # print("yz value:",hex(y.value),hex(z.value))
    sum_value =c_int32(0)
    i = 0
    delta = 0x9e3779b9
    a, b, c, d = struct.unpack('<IIII',
                               k)  # struct.unpack('I',str.encode(k[0])+str.encode(k[1])+str.encode(k[2])+str.encode(k[3]))
   # print("abcd value:", hex(a), hex(b),hex(c),hex(d))
    #		print("%d"%a,"%d"%b)
    for i in range(32):
        sum_value.value += delta
        #sum_value &= 0xFFFFFFFF
        y.value += ((z.value << 4) + a) ^ (z.value + sum_value.value) ^ ((z.value >> 5) + b)
        #y &= 0xFFFFFFFF
        z.value += ((y.value << 4) + c) ^ (y.value + sum_value.value) ^ ((y.value >> 5) + d)
        #z &= 0xFFFFFFFF
    # print(y,z)
    #		print(y,z)
    r = struct.pack('<ii', y.value, z.value)
    return r


# **********************************************************************************************
def encrypt(src, key):
    a = 0
    i = 0
    num = 0
    size_src = len(src)
    # 将明文补足为8字节的倍数
    a = size_src % 8
    if a != 0:
        for i in range(8 - a):
            src[size_src] = 0x00
            size_src += 1
    # 加密
    num = size_src / 8
    s = (b'')
    for i in range(int(num)):
        # string = stmp(src
        s += tea_encrypt(src[i * 8:i * 8 + 8], key)#encipher(src[i * 8:i * 8 + 8], key)#
    # HexShow(s)
    #	HexShow(tea_encrypt(s[0:8],key))
    return s


# *********************************

def tea_decryt(v, k):
    y = c_int32(struct.unpack('<i', v[0:4])[0])
    z = c_int32(struct.unpack('<i', v[4:])[0])
    # print("yz value:",hex(y.value),hex(z.value))
    sum_value = c_int32(0xC6EF3720)

    i = 0
    delta = 0x9e3779b9
    a, b, c, d = struct.unpack('<iiii', k)
    for i in range(32):
        z.value -= ((y.value << 4) + c) ^ (y.value + sum_value.value) ^ ((y.value >> 5) + d)
        y.value -= ((z.value << 4) + a) ^ (z.value + sum_value.value) ^ ((z.value >> 5) + b)
        sum_value.value -= delta
    # print(y,z)
    #		print(y,z)
    r = struct.pack('<ii', y.value, z.value)
    return r

# *********************************
#
def decrypt(src, key):
    a = 0
    i = 0
    num = 0
    size_src = len(src)
    # 将明文补足为8字节的倍数
    a = size_src % 8
    if a != 0:
        for i in range(8 - a):
            src[size_src] = 0x00
            size_src += 1
    # 加密
    num = size_src / 8
    s = (b'')
    for i in range(int(num)):
        s += tea_decryt(src[i * 8:i * 8 + 8], key)

    return s

 # ******************************************************************************