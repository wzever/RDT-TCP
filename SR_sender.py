from email import message
from socket import *
import json
import time

from sympy import false, true
from utils import Timer


def notcorrupt(rcvpkt):
    return rcvpkt['checksum']

def make_pkt(pktID, data, checksum):
    sendData = {}
    sendData['pktID'] = pktID
    sendData['data'] = data
    sendData['checksum'] = checksum
    sendMessage = json.dumps(sendData)
    return sendMessage

def getacknum(rcvpkt):
    return rcvpkt['pktID']

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
        self.run()

    def run(self):
        global timer
        ACK_GROUP = [False] * L
        SEND_GROUP = [False] * L
        CACHE = [''] * N
        base = 0    # base 表示窗口中最早发送字符的序列号

        ''' 
        保证对原字符串 message， 任意循环中 message[base+i] 对应的序列号为 (base+i)%L ,缓存对应 CACHE[i](如果未被覆盖)
        计时器对应timer[i]
        '''
        while self.message or base != self.LEN % L:
            for i in range(N):
                if self.message and not SEND_GROUP[(base + i) % L]:
                    print("Packege{}  MessagePkt:{} has been sent".format(  (base + i)%L  ,self.message[0]) )
                    """
                    发送分组，启动计时器，缓存，更新message
                    your code here
                    """
                    CACHE[i] = self.message[0]
                    timer[i].start_timer()
                    sndpkt = make_pkt((base + i)%L, self.message[0], True)
                    clientSocket.sendto(sndpkt.encode(),('localhost',serverPort))   
                    SEND_GROUP[(base + i) % L] = true
                    self.message = self.message[1:]                 
                if timer[i].active and timer[i].if_timeout():
                    print("Timeout. Resend the package")
                    # 注：SR 中超时事件只重发超时事件的分组
                    print("Packege{}  MessagePkt:{} has been sent".format(  (base + i)%L  ,CACHE[i]  )) 
                    """
                    超时事件，重发分组，重启计时器
                    your code here
                    """
                    timer[i].start_timer()
                    sndpkt = make_pkt((base + i)%L, CACHE[i], True)
                    clientSocket.sendto(sndpkt.encode(),('localhost',serverPort))  
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
                    ID = getacknum(rcvpkt)
                    timer[(ID + L - base) % L].stop_timer()
                    ACK_GROUP[ID] = true

            except BlockingIOError:
                print("Waiting ACK...")
                time.sleep(1)
                continue

            # 每次循环中检测窗口是否允许滑动
            while base < self.LEN and ACK_GROUP[base%L]:
                # 计时器, 缓存, ACK_GROUP, SEND_GROUP, base 更新 
                """
                your code here
                """  
                timer[0].stop_timer()
                timer = timer[1:] + [timer[0]]
                CACHE = CACHE[1:] + [CACHE[0]]
                ACK_GROUP[base % L] = false
                SEND_GROUP[base % L] = false
                base = (1+base)%L
                
            
        print("Finish")
        while input("回车键退出"):
            pass


if __name__ == '__main__':
    print("SR 协议 sender 端实例化：")
    sender_ = sender()
