import threading
import socket



#creat IPv4 and tcp socket
skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#listening the port
skt.bind(('127.0.0.1', 10001))

skt.listen(5)#most waiting number is equal 5
print("waiting listening...")


#define the thread process block
def tcpclientlink(sock, addr):
    print("Accept new connection from %s:%s..."%addr)
    sock.send('welcome!'.encode(encoding='utf-8'))
    # timeout = 30s
 #   sock.settimeout(30000)
    while True:
        data = sock.recv(1024)
        if data == 'exit'.encode(encoding='utf-8')or not data:
            sock.send('Goodbye!'.encode(encoding='utf-8'))
            break
        print(data,'\n')
        sock.send(data)
    sock.close
    print("Connection from %s:%s closed"%addr)

while True:
#accept new link
    sock, addr = skt.accept()
# creat new thread to process msg
    thrd = threading.Thread(target= tcpclientlink,args=(sock, addr))
    thrd.start()
