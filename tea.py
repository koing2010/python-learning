from struct import pack as _pack 
from struct import unpack as _unpack 
from binascii import b2a_hex, a2b_hex 

from random import seed 
from random import randint as _randint 

__all__ = ['encrypt', 'decrypt'] 

seed() 

op = 0xffffffff

def xor(a, b): 
   a1,a2 = _unpack('>LL', a[0:8]) 
   b1,b2 = _unpack('>LL', b[0:8]) 
   r = _pack('>LL', ( a1 ^ b1) & op, ( a2 ^ b2) & op) 
   return r 


def code(v, k): 
   """ 
   TEA coder encrypt 64 bits value, by 128 bits key, 
   QQ do 16 round TEA. 
   To see: 
   http://www.ftp.cl.cam.ac.uk/ftp/papers/djw-rmn/djw-rmn-tea.html . 
	
   TEA 加密,  64比特明码, 128比特密钥, qq的TEA算法使用16轮迭代 
   具体参看 
   http://www.ftp.cl.cam.ac.uk/ftp/papers/djw-rmn/djw-rmn-tea.html 

   >>> c = code('abcdefgh', 'aaaabbbbccccdddd') 
   >>> b2a_hex(c) 
   'a557272c538d3e96' 
   """ 
   n=16  #qq use 16 
   delta = 0x9e3779b9
   k = _unpack('>LLLL', k[0:16]) 
   y, z = _unpack('>LL', v[0:8]) 
   s = 0 
   for i in xrange(n): 
	   s += delta 
	   y += (op &(z<<4))+ k[0] ^ z+ s ^ (op&(z>>5)) + k[1] ; 
	   y &= op 
	   z += (op &(y<<4))+ k[2] ^ y+ s ^ (op&(y>>5)) + k[3] ; 
	   z &= op 
   r = _pack('>LL',y,z) 
   return r 

def encrypt(v, k): 
   """ 
   Encrypt Message follow QQ's rule. 
   用QQ的规则加密消息 

   v is the message to encrypt, k is the key 
   参数 v 是被加密的明文, k是密钥 
   fill char is some random numbers (in old QQ is 0xAD) 
   填充字符数是随机数, (老的QQ使用0xAD) 
   fill n char's n = (8 - (len(v)+2)) %8 + 2 
   填充字符的个数 n = (8 - (len(v)+2)) %8 + 2 
   ( obviously, n is 2 at least, n is 2-9) 
   ( 显然, n至少为2, 取2到9之间) 

   then insert (n - 2)|0xF8 in the front of the fill chars 
   然后在填充字符前部插入1字节, 值为 ((n - 2)|0xF8) 
   to record the number of fill chars. 
   以便标记填充字符的个数. 
   append 7 '\0' in the end of the message. 
   在消息尾部添加7字节'\0' 
	
   thus the lenght of the message become filln + 8 + len(v), 
   因此消息总长变为 filln + 8 + len(v), 
   and it == 0 (mod 8) 
   他模8余0(被8整除) 

   Encrypt the message . 
   加密这段消息 
   Per 8 bytes, 
   每8字节, 
   the result is: 
   规则是 
	
   r = code( v ^ tr, key) ^ to   (*) 

   code is the QQ's TEA function. 
   code函数就是QQ 的TEA加密函数. 
   v is 8 bytes data to encrypt. 
   v是被加密的8字节数据 
   tr is the result in preceding round. 
   tr是前次加密的结果 
   to is the data coded in perceding round, is v_pre ^ r_pre_pre 
   to是前次被加密的数据, 等于 v_pre ^ r_pre_pre 

   For the first 8 bytes 'tr' and 'to' is zero. 
   对头8字节, 'tr' 和 'to' 设为零 
	
   loop and loop, 
   不断循环, 
   that's end. 
   结束. 
	
   >>> en = encrypt('', b2a_hex('b537a06cf3bcb33206237d7149c27bc3')) 
   >>> decrypt(en,  b2a_hex('b537a06cf3bcb33206237d7149c27bc3')) 
   '' 
   """ 
   ##FILL_CHAR = chr(0xAD) 
   END_CHAR = '\0' 
   FILL_N_OR = 0xF8 
   vl = len(v) 
   filln = (8-(vl+2))%8 + 2; 
   fills = '' 
   for i in xrange(filln): 
	   fills = fills + chr(_randint(0, 0xff)) 
   v = ( chr((filln -2)|FILL_N_OR) 
		 + fills 
		 + v 
		 + END_CHAR * 7) 
   tr = '\0'*8 
   to = '\0'*8 
   r = '' 
   o = '\0' * 8 
   #print 'len(v)=', len(v) 
   for i in xrange(0, len(v), 8): 
	   o = xor(v[i:i+8], tr) 
	   tr = xor( code(o, k), to) 
	   to = o 
	   r += tr 
   return r 

def decrypt(v, k): 
   """ 
   DeCrypt Message 
   消息解密 
	
   by (*) we can find out follow easyly: 
   通过(*)式,我们可以容易得发现(明文等于): 
	
   x  = decipher(v[i:i+8] ^ prePlain, key) ^ preCyrpt 
	
   prePlain is pre 8 byte to be code. 
   perPlain 是被加密的前8字节 
	
   Attention! It's v per 8 byte value xor pre 8 byte prePlain, 
   注意! 他等于前8字节数据异或上前8字节prePlain, 
   not just per 8 byte. 
   而不只是前8字节. 
   preCrypt is pre 8 byte Cryped. 
   perCrypt 是前8字节加密结果. 

   In the end of deCrypte the raw message, 
   在解密完原始数据后, 
   we have to cut the filled bytes which was append in encrypt. 
   我们必须去除在加密是添加的填充字节. 

   the number of the filling bytes in the front of message is 
   填充在消息头部的字节数是 
   pos + 1. 
	
   pos is the first byte of deCrypted --- r[0] & 0x07 + 2 
   pos等于解密后的第一字节 --- r[0] & 0x07 + 2 

   the end of filling aways is 7 zeros. 
   尾部填充始终是7字节零. 
   we can test the of 7 bytes is zeros, to make sure it is right. 
   我们可以通测试最后7字节是零, 来确定它是正确的. 
	
   so return r[pos+1:-7] 
   所以返回 r[pos+1:-7] 

   >>> r = encrypt('', b2a_hex('b537a06cf3bcb33206237d7149c27bc3')) 
   >>> decrypt(r, b2a_hex('b537a06cf3bcb33206237d7149c27bc3')) 
   '' 
   >>> r = encrypt('abcdefghijklimabcdefghijklmn', b2a_hex('b537a06cf3bcb33206237d7149c27bc3')) 
   >>> decrypt(r, b2a_hex('b537a06cf3bcb33206237d7149c27bc3')) 
   'abcdefghijklimabcdefghijklmn' 
   >>> import md5 
   >>> key = md5.new(md5.new('python').digest()).digest() 
   >>> data='8CE160B9F312AEC9AC8D8AEAB41A319EDF51FB4BB5E33820C77C48DFC53E2A48CD1C24B29490329D2285897A32E7B32E9830DC2D0695802EB1D9890A0223D0E36C35B24732CE12D06403975B0BC1280EA32B3EE98EAB858C40670C9E1A376AE6C7DCFADD4D45C1081571D2AF3D0F41B73BDC915C3AE542AF2C8B1364614861FC7272E33D90FA012620C18ABF76BE0B9EC0D24017C0C073C469B4376C7C08AA30' 
   >>> data = a2b_hex(data) 
   >>> b2a_hex(decrypt(data, key)) 
   '00553361637347436654695a354d7a51531c69f1f5dde81c4332097f0000011f4042c89732030aa4d290f9f941891ae3670bb9c21053397d05f35425c7bf80000000001f40da558a481f40000100004dc573dd2af3b28b6a13e8fa72ea138cd13aa145b0e62554fe8df4b11662a794000000000000000000000000dde81c4342c8966642c4df9142c3a4a9000a000a' 
	
   """ 
   l = len(v) 
   #if l%8 !=0 or l<16: 
   #    return '' 
   prePlain = decipher(v, k) 
   pos = (ord(prePlain[0]) & 0x07) +2 
   r = prePlain 
   preCrypt = v[0:8] 
   for i in xrange(8, l, 8): 
	   x = xor(decipher(xor(v[i:i+8], prePlain),k ), preCrypt) 
	   prePlain = xor(x, preCrypt) 
	   preCrypt = v[i:i+8] 
	   r += x 
   if r[-7:] != '\0'*7: return None 
	

   return r[pos+1:-7] 

def decipher(v, k): 
   """ 
   TEA decipher, decrypt  64bits value with 128 bits key. 
   TEA 解密程序, 用128比特密钥, 解密64比特值 

   it's the inverse function of TEA encrypt. 
   他是TEA加密函数的反函数. 

   >>> c = code('abcdefgh', 'aaaabbbbccccdddd') 
   >>> decipher( c, 'aaaabbbbccccdddd') 
   'abcdefgh' 
   """ 

   n = 16 
   y, z = _unpack('>LL', v[0:8]) 
   a, b, c, d = _unpack('>LLLL', k[0:16]) 
   delta = 0x9E3779B9; 
   s = (delta << 4)&op 
   for i in xrange(n): 
	   z -= ((y<<4)+c) ^ (y+s) ^ ((y>>5) + d) 
	   z &= op 
	   y -= ((z<<4)+a) ^ (z+s) ^ ((z>>5) + b) 
	   y &= op 
	   s -= delta 
	   s &= op 
   return _pack('>LL', y, z) 
