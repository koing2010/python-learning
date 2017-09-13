#
import socket
import time
import threading

SendStr = (b'\x08\x7D\x7B\xBB\x0D\x00\x4B\x12\x00')


s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.connect(('47.94.155.129',10000))

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
while True:
    print("send")
    s.send(SendStr)
    print(time.strftime('end %Y-%m-%d %H:%M:%S', time.localtime()))
    time.sleep(5)

thrd.join()
s.close()
print("send over")