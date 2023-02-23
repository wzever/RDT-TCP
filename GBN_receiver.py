import json
from socket import *
import time
import random
from utils import simulator


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
L = 8   # 序号长度

serverSocket = socket(AF_INET, SOCK_DGRAM)
serverPort = 15000
serverSocket.bind(('', serverPort))


class receiver:
    def __init__(self):
        self.strBuffer = ''
        self.run()

    def run(self):
        while True:
            if len(self.strBuffer) != 0 and self.strBuffer[-1] == '\n':
                print("The received messages through GBN:\n{}\n".format(self.strBuffer))
                break
            base = len(self.strBuffer)      # 已接受的字符串长度
            rcvpkt, address = serverSocket.recvfrom(1024)
            rcvpkt = json.loads(rcvpkt.decode())
            rcvpkt = simulator(rcvpkt)
            if rcvpkt is None:
                print("Package lost.", '\n')
                continue
            print(rcvpkt, '\n')

            if notcorrupt(rcvpkt) and rcvpkt['pktID'] == base % L:
                message = rcvpkt['data'].upper()
                self.strBuffer = self.strBuffer + message
                print('strBuffer:',self.strBuffer)
                """
                    生成 ACK 并发送
                    code here
                """
                # time.sleep(random.uniform(40,60)/1000)
                sndpkt = make_pkt(rcvpkt['pktID'], 'ACK', True)
                serverSocket.sendto(sndpkt.encode(),address)
            else:
                """
                    生成 ACK 并发送
                    code here
                """
                sndpkt = make_pkt(base % L - 1, 'ACK', True)
                serverSocket.sendto(sndpkt.encode(),address)
        while input("回车键退出"):
            pass


if __name__ == '__main__':
    print("GBN 协议 receiver 端实例化：")
    receiver_ = receiver()
