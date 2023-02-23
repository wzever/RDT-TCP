import json
from socket import *

from pymysql import NULL
from utils import simulator


def notcorrupt(rcvpkt):
    return rcvpkt['checksum']

def notempty(rcvpkt):
    return (rcvpkt['data'] != NULL)


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

# 参数设置
N = 4   # 窗口长度
L = 8   # 序号长度

serverSocket = socket(AF_INET, SOCK_DGRAM)
serverPort = 15000
serverSocket.bind(('', serverPort))

class receiver:
    def __init__(self):
        self.strBuffer = ''
        self.ACK = json.dumps('ACK')
        self.FIN = json.dumps('FIN')
        
        self.run()


    # 客户端应该无法选择主动选择调用函数，应对包进行分类？
    def Seq_ACK(self):
        buffer = [0]*101
        while True:
            if len(self.strBuffer) != 0 and self.strBuffer[-1] == '\n':
                print("The received messages through GBN:\n{}\n".format(self.strBuffer))
                self.strBuffer = ''
                break
            rcvpkt, address = serverSocket.recvfrom(1024)
            rcvpkt = json.loads(rcvpkt.decode())
            # rcvpkt = simulator(rcvpkt)
            if rcvpkt is None:
                print("Package lost.")
                continue
            print(rcvpkt)

            if notcorrupt(rcvpkt):
                ACK = getSeq(rcvpkt) + 1
                print(rcvpkt)
                Seq = getack(rcvpkt)

                if notempty(rcvpkt):
                    # 对于seq的buffer如何处理？      
                    buffer[ACK - 1] = rcvpkt['data']
                    self.strBuffer += buffer[ACK-1]
                    sndpkt2 = make_pkt(Seq, ACK, rcvpkt['data'], True)
                    serverSocket.sendto(sndpkt2.encode(),address)
            # 发生错误后的操作 ： SR？


    def handshake(self):
        # print('server state : CLOSED')
        print('server state : LISTEN','\n') #此处应该写在创建监听套接字后

        SYN = 1
        hand_pkt1, address = serverSocket.recvfrom(1024)
        hand_pkt1 = json.loads(hand_pkt1.decode())
        client_isn = hand_pkt1['seq']
        ''' 分配缓存

        '''
        server_isn = 100 # 服务器初始序号
        sndhand = make_hand(SYN,server_isn,client_isn+1)
        serverSocket.sendto(sndhand.encode(),address)
        print('SYN received, SYN & ACK sent')
        print('server state : SYN_RCVD','\n')

        hand_pkt3, address = serverSocket.recvfrom(1024)
        hand_pkt3 = json.loads(hand_pkt3.decode())
        client_isn = hand_pkt3['seq'] - 1
        server_isn = hand_pkt3['ack'] - 1
        print('ACK received')
        print('server state : ESTABLISHED','\n')


    def end_handshake(self):
        rcvpkt, address = serverSocket.recvfrom(1024)
        rcvpkt = json.loads(rcvpkt.decode())   

        # 是否要加入纠错

        #
        if rcvpkt == 'FIN':
            serverSocket.sendto(self.ACK.encode(),address)
            print('FIN received, ACK sent')
            print('server state : CLOSE_WAIT','\n')

            serverSocket.sendto(self.FIN.encode(),address)
            print('FIN sent')
            print('server state : LAST_ACK','\n')

            rcvpkt, address = serverSocket.recvfrom(1024)
            print('ACK received')
            print('server state : CLOSED','\n')

    def run(self):
        self.handshake()
        self.Seq_ACK()
        self.end_handshake()


if __name__ == '__main__':
    print("SR 协议 receiver 端实例化：")
    receiver_ = receiver()
