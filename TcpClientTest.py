#
import socket
import time
import threading

SendStr = (b'\x08\x7D\x7B\xBB\x0D\x00\x4B\x12\x00')


s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.connect(('47.94.155.129',10001))#(('127.0.0.1', 10001))#

#define the thread
def thread_TcpRX():
    print(thread_TcpRX.__name__)
    buffer = []
    while 1:
        d = s.recv(1024)
        print(d)
        if d:
            print("d = ",d)
            buffer.append(d)
            print(buffer)
            if buffer[0] == 'Goodbye!'.encode(encoding='utf-8'):#buffer is list
                print("threading exit!")
                break
            buffer = []
        else:
            time.sleep(5)
            buffer = []
'''
            while 1:
               d = s.recv(1024)
               print(d)
               if d:
                   buffer.append(d)
               else:
                   break
            print(buffer)
'''


thrd = threading.Thread(target=thread_TcpRX,name='tcprx')
thrd.start()
n = 0
while True:
    n =n +1
    if n > 5:
        s.send('exit'.encode(encoding='utf-8'))
        time.sleep(1)
        break
    print("send")
    s.send(SendStr)
    print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
    time.sleep(5)

thrd.join()
s.close()
print("send over")