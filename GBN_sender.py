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
timer = Timer(2)    # GBN 协议中仍然只使用一个计时器，用于计时最早的已发送还未被确认的分组的计时器


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

                    sndpkt = make_pkt((base + i) % L, self.message[0], True)
                    clientSocket.sendto(sndpkt.encode(), ('localhost',serverPort))
                    print("Packege{}  MessagePkt:{} has been sent".format((base + i) % L, self.message[0]))

                    timer.start_timer() 
                    SEND_GROUP[(base + i) % L] = True 
                    CACHE[i] = self.message[0]
                    self.message = self.message[1:]
                    
                if timer.if_timeout():
                    print("Timeout. Resend the package")

                    for j in range(i, N):
                        sndpkt = make_pkt((base + j) % L, CACHE[j], True)
                        clientSocket.sendto(sndpkt.encode(), ('localhost',serverPort))
                        print("Packege{}  MessagePkt:{} has been sent".format((base + j) % L, CACHE[j]))
                    timer.start_timer()     # 重启计时器
            try:
                rcvpkt = clientSocket.recv(1024)
                rcvpkt = json.loads(rcvpkt.decode())
                print("Receive: ", rcvpkt, '\n')

                # 收到分组并滑动窗口
                if notcorrupt(rcvpkt):
                    base = rcvpkt['pktID'] + 1
                    # 重启计时器
                    timer.start_timer()
            except BlockingIOError:
                print("Waiting ACK...")
                time.sleep(1)
                continue
        timer.stop_timer()
        print("Finish")
        while input("回车键退出"):
            pass


if __name__ == '__main__':
    print("GBN 协议 sender 端实例化：")
    sender_ = sender()
