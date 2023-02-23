import json
from pydoc import cli
import random
import time
from email import message
from socket import *

from pymysql import NULL
from sympy import false, true

from utils import Timer


def notcorrupt(rcvpkt):
    return rcvpkt['checksum']

# Seq : 序号  ACK ： 确认号
def make_pkt(Seq, ACK, data, checksum):
    sendData = {}
    sendData['Seq'] = Seq
    sendData['ACK'] = ACK
    sendData['data'] = data
    sendData['checksum'] = checksum
    sendMessage = json.dumps(sendData)
    return sendMessage

def make_hand(SYN,seq,ack=NULL):
    sendData = {}
    sendData['SYN'] = SYN
    sendData['seq'] = seq
    sendData['ack'] = ack
    sendMessage = json.dumps(sendData)
    return sendMessage   


def getack(rcvpkt):
    return rcvpkt['ACK']

def getSeq(rcvpkt):
    return rcvpkt['Seq']

def randomselect():
    return random.randint(1,100)


# 参数设置
N = 4   # 窗口长度
L = 8   # 序号长度

serverName = gethostname()
serverPort = 15000

clientSocket = socket(AF_INET, SOCK_DGRAM)
clientSocket.setblocking(False)
timer = [Timer(2) for i in range(N)]    # SR 协议中需要对每个分组创造计时器


class sender:
    def __init__(self):
        self.message = input("Input sentence: \n")
        self.message = self.message + '\n'
        self.LEN = len(self.message)     # 序号范围 0 ~ len(self.message) - 1
        self.ACK = json.dumps('ACK')
        self.FIN = json.dumps('FIN')
        self.run()

    def Seq_ACK(self):
        Seq = 0
        ACK = 100
        while Seq < len(self.message):
            sndpkt1 = make_pkt(Seq,ACK,self.message[Seq],True)
            clientSocket.sendto(sndpkt1.encode(),('localhost',serverPort))
            print("Send: ", sndpkt1, '\n')

            try:
                rcvpkt = clientSocket.recv(1024)
                rcvpkt = json.loads(rcvpkt.decode())
                print("Receive: ", rcvpkt, '\n')
                if notcorrupt(rcvpkt):
                    """
                    读取包，进行分组确认
                    停计时器
                    your code here
                    
                    """
                    
                    Seq = getack(rcvpkt)
                    ACK = getSeq(rcvpkt) + 1

                    # 应有计时器，纠错部分
                    # timer[ACK-1].stop_timer()
                    
                    sndpkt3 = make_pkt(Seq,ACK,NULL,True)
                    clientSocket.sendto(sndpkt3.encode(),('localhost',serverPort))

            except BlockingIOError:
                print("Waiting ACK...")
                time.sleep(1)
                continue

    
    def handshake(self):
        # print('client state : CLOSED') # 开始时的状态是否为CLOSED？感觉问题不大，保持一致即可
        client_isn = randomselect()
        SYN = 1
        sndhand1 = make_hand(SYN,client_isn)
        clientSocket.sendto(sndhand1.encode(),('localhost',serverPort))
        print('SYN sent')
        print('client state : SYN_SENT','\n')

        rcvpkt = clientSocket.recv(1024)
        rcvpkt = json.loads(rcvpkt.decode())

        seq = rcvpkt['ack']
        ack = rcvpkt['seq']
        sndhand3 = make_hand(0,seq,ack)
        clientSocket.sendto(sndhand3.encode(),('localhost',serverPort))
        print('SYN & ACK received, ACK sent')
        print('client state : ESTABLISHED','\n')


    def end_handshake(self):
        clientSocket.sendto(self.FIN.encode(),('localhost',serverPort))
        print('FIN sent')
        print('client state : FIN_WAIT_1','\n')

        flag =false
        while True:
            rcvpkt = clientSocket.recv(1024)
            rcvpkt = json.loads(rcvpkt.decode())
            # 纠错
            #
            if not flag and rcvpkt == 'ACK':
                flag = True
                print('ACK received')
                print('client state : FIN_WAIT_2','\n')
                continue
            if flag and rcvpkt == 'FIN':
                clientSocket.sendto(self.ACK.encode(),('localhost',serverPort)) 
                print('FIN received, ACK sent')  
                print('client state : TIME_WAIT','\n')   
                print('Wait for 30s ... ','\n')          
                time.sleep(3) #实际应等待30s
                print('client state : CLOSED','\n')
                return 

    def run(self):
        self.handshake()
        self.Seq_ACK()
        self.end_handshake()


if __name__ == '__main__':
    print("SR 协议 sender 端实例化：")
    sender_ = sender()
