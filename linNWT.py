import serial
import time
import threading
import queue


START_STATE = 0
CMD_STATE = 1
LEN_STATE = 3
DATA_STATE = 4

class myThread (threading.Thread):
    def __init__(self, threadID, name, q):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.q = q
    def run(self):
        print("Starting " + self.name)
        if self.threadID is 1:
            process_data(self.name, self.q)
        elif self.threadID is 2:
            txdata(self.name, self.q)
        else:
            print("Thread Start ERRO!")
        print("Exiting " + self.name)

# usart tx data
def txdata(threadName, q):
        print(threadName + "start")
        while (1):
            while not sendQueue.empty():
                txda = sendQueue.get()
                s.write(txda)
                HexShow("txthread:", txda)
                time.sleep(2)

# usart rx data
def process_data(threadName, q):
        print(threadName + "start")
        RxStatus = 0
        LenToken = 0
        LenTemp = 0
        while True:
            while s.inWaiting() == 0:
                pass
            byte = s.read(1)

            print(byte)
            if  RxStatus == START_STATE:
                if byte[0] == 0x8F:
                    print("SF")
                    RxStatus = CMD_STATE
                    string = byte
            elif RxStatus == CMD_STATE:
                if byte =='f'.encode(encoding='utf-8'):
                    print("set VFO")
                    LenToken = 22
                if byte == 'x'.encode(encoding='utf-8'):
                    print('Sweep n with AD8307')
                    LenToken = 22
                    string = byte
                    workQueue.put(string)
                if byte == 'w'.encode(encoding='utf-8'):
                    print('Sweep n with the AD8361')
                    LenToken = 22
                if byte == 'v'.encode(encoding='utf-8'):
                    print('Query version of the firmware')
                    LenToken = 25
                if byte == 'a'.encode(encoding='utf-8'):
                 RxStatus =  LEN_STATE

            elif RxStatus == LEN_STATE:
                RxStatus = START_STATE

# display hex string
def HexShow(i_string):
    hex_string = ''
    hLen = len(i_string)
    for i in range(hLen):
        hvol = i_string[i]
        hhex = '0x%02X' % (hvol)
        hex_string += hhex + ' '
    # print('ReceiveBytes: %i_string' % (hex_string))
    print('ReceiveBytes:', hex_string, '  total:', hLen)


Comnumb = 'com13'
#Comnumb = input('输入串口号(如com4):')
s = serial.Serial(Comnumb, 57600)
string = ' '

queueLock = threading.Lock()
workQueue = queue.Queue(maxsize = 10)
sendQueue = queue.Queue(maxsize = 10)

Rxthrd = myThread(1,'uartRxThread',workQueue)
Rxthrd.start()# start threading
#Rxthrd.join()
Txthrd = myThread(2,'uartTxThread',sendQueue)
Txthrd.start()# start threading
#Rxthrd.join()

# thrd = threading.Thread(target=MyTxThread,name='koing2010')
# thrd.start()
while (1) :

    #print(type(rx_string))
    if not workQueue.empty():
        rx_string = workQueue.get()
    else:
        continue
    print(type(rx_string))
    if rx_string == 'x'.encode(encoding='utf-8'):
        for i in range(1000):
            s.write(bytes.fromhex("C7 01"))  # adc value  ref_voltage = 5V use 10bits ADC,
            print(i)
            time.sleep(0.05)

s.close()
# thrd.join()
