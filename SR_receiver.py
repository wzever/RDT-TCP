import json
from socket import *
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


def getseqnum(rcvpkt):
    return rcvpkt['pktID']

# 参数设置
N = 4   # 窗口长度
L = 8   # 序号长度

serverSocket = socket(AF_INET, SOCK_DGRAM)
serverPort = 15000
serverSocket.bind(('', serverPort))

class receiver:
    def __init__(self):
        self.strBuffer = ''
        self.run()

    def run(self):
        """
        参考 GBN.receiver.py 和 SR.sender.py 实现接收端代码 
        your code here
        """
        rcv_base = 0
        buffer = dict()

        while True:
            if len(self.strBuffer) != 0 and self.strBuffer[-1] == '\n':
                print("The received messages through GBN:\n{}\n".format(self.strBuffer))
                self.strBuffer = ''
                break

            rcvpkt, address = serverSocket.recvfrom(1024)
            rcvpkt = json.loads(rcvpkt.decode())
            rcvpkt = simulator(rcvpkt)
            if rcvpkt is None:
                print("Package lost.")
                continue
            print(rcvpkt)

            if notcorrupt(rcvpkt):
                pktseqnum = getseqnum(rcvpkt)
                if pktseqnum >= rcv_base - N and pktseqnum < rcv_base   :
                    sndpkt = make_pkt(pktseqnum % L, 'ACK', True)
                    serverSocket.sendto(sndpkt.encode(),address)      
                if (pktseqnum >= rcv_base and pktseqnum < rcv_base + N) or L + pktseqnum < rcv_base + N:
                    sndpkt = make_pkt(pktseqnum, 'ACK', True)
                    serverSocket.sendto(sndpkt.encode(),address) 
                    buffer[pktseqnum] = rcvpkt['data']
                    print(" buffered.")
                    if rcv_base == pktseqnum:
                        i = pktseqnum
                        while i in buffer.keys():
                            message = buffer[i].upper()
                            self.strBuffer = self.strBuffer + message
                            print('packet', i, " delivered.")
                            i = (1+i) % L
                        buffer.clear()
                        rcv_base = i

        while input("回车键退出"):
            pass


if __name__ == '__main__':
    print("SR 协议 receiver 端实例化：")
    receiver_ = receiver()
