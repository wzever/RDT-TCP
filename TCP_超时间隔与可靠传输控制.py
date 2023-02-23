import matplotlib.pyplot as plt
import numpy as np
from socket import *
import json
import time

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


# 参数设置
N = 4   # 窗口长度
L = 8   # 序号长度

serverName = gethostname()
serverPort = 15000

clientSocket = socket(AF_INET, SOCK_DGRAM)
clientSocket.setblocking(False)
time_out = 1
est_rtt, dev_rtt = 0, 0
alpha, beta = 0.125, 0.25
timer = Timer(time_out)    # GBN 协议中仍然只使用一个计时器，用于计时最早的已发送还未被确认的分组的计时器
xaxis = []
yaxis_est = []
yaxis_spl = []
y_timeout = []
y_dev = []
begin_time = time.time()

class sender:
    def __init__(self):
        self.message = input("Input sentence: \n")
        self.message = self.message + '\n'

        self.LEN = len(self.message)

        self.run()

    def run(self):
        SEND_GROUP = [False] * L    # 序号范围 0 ~ L - 1
        CACHE = [''] * N    # 窗口内分组的缓存
        base = 0    # base 表示窗口中最早发送字符的序列号

        while self.message or base != self.LEN % L:
            for i in range(N):
                if self.message and not SEND_GROUP[(base + i) % L]:
                    """
                        生成分组并发送
                        Your Code Here
                    """
                    sndpkt = make_pkt((base + i) % L, self.message[0], True)
                    clientSocket.sendto(sndpkt.encode(), ('localhost',serverPort))
                    print("Packege{}  MessagePkt: {} has been sent".format((base + i) % L, self.message[0]))

                    timer.start_timer() 
                    SEND_GROUP[(base + i) % L] = True 
                    CACHE[i] = self.message[0]
                    self.message = self.message[1:]
                    
                if timer.if_timeout():
                    print("Timeout. Resend the package")

                    for j in range(i, N):
                        if CACHE[j]:
                            """
                                重传分组
                                Your Code Here
                            """
                            sndpkt = make_pkt((base + j) % L, CACHE[j], True)
                            clientSocket.sendto(sndpkt.encode(), ('localhost',serverPort))
                            print("Packege{}  MessagePkt: {} has been sent".format((base + j) % L, CACHE[j]))
                    global time_out
                    time_out *= 2  # 超时间隔加倍
                    timer.target = time_out
                    timer.start_timer()     # 重启计时器
            try:
                rcvpkt = clientSocket.recv(1024)
                rcvpkt = json.loads(rcvpkt.decode())
                print("Receive: ", rcvpkt, '\n')

                # 收到分组并滑动窗口
                if notcorrupt(rcvpkt) and rcvpkt['pktID'] == base % L:                    
                    base = (rcvpkt['pktID'] + 1) % L
                    CACHE = CACHE[1:] + ['']
                    if base == 0:
                        SEND_GROUP = [False] * L
                    # 重启计时器
                    global est_rtt, dev_rtt
                    if not est_rtt:
                        est_rtt = timer.rtt()
                    else:    # 计算 est_rtt / dev_rtt 
                        est_rtt = (1 - alpha) * est_rtt + alpha * timer.rtt()
                        dev_rtt = (1 - beta) * dev_rtt + beta * abs(timer.rtt() - est_rtt)
                        xaxis.append(time.time() - begin_time)
                        yaxis_spl.append(1000*timer.rtt()) 
                        yaxis_est.append(1000*est_rtt)
                        y_dev.append(1000*dev_rtt)
                        y_timeout.append(1000*time_out)
                    time_out = est_rtt + 4 * dev_rtt
                    # time_out = 1
                    timer.target = time_out
                    timer.start_timer()
            except BlockingIOError:
                print("Waiting ACK...")
                time.sleep(0.5)
                continue
        timer.stop_timer()
        print("Finish")
        print(time.time()-begin_time)
        while input("回车键退出"):
            pass

if __name__ == '__main__':
    print("GBN 协议 sender 端实例化：")
    sender_ = sender()
    plt.rcParams['font.sans-serif']=['SimHei']
    plt.subplot(121)
    plt.title('RTT样本和RTT估计')
    plt.xlabel("时间(s)")
    plt.ylabel("RTT(ms)")
    plt.plot(xaxis,yaxis_est,'r',label = '估计RTT',linewidth=3.0)
    plt.plot(xaxis,yaxis_spl, label = '样本RTT',linewidth=1.0)
    plt.plot(xaxis,y_dev, label = 'RTT偏差',linewidth=1.0)
    plt.legend()
    
    plt.subplot(122)
    plt.title('TimoutInterval')
    plt.xlabel("时间(s)")
    plt.ylabel("TimeoutInterval(ms)")
    plt.plot(xaxis,y_timeout,label='Timeout interval')
    plt.legend()
    
    plt.show()