import numpy as np 
from matplotlib import pyplot as plt 
import random
plt.rcParams['font.sans-serif'] = ['SimHei']

cwin_reno = eval(input('Initial window size:')) 
ssthresh = eval(input('Initial ssthresh:')) 
cnt = eval(input("Total round: ")) 
cwin_tahoe = cwin_reno
th_tahoe = ssthresh

# Start Simulating
timeout = [ random.random()>0.95 for i in range(1,cnt+1)]
retrans = [ random.random()<0.1 for i in range(1,cnt+1)]

trans_rnd, y1, y2 = [] ,[], []

# TCP Reno
for rnd in range(1,cnt):

    print(rnd, "-th round", " cwnd: ", cwin_reno)

    trans_rnd.append(rnd)
    y1.append(cwin_reno)
    
    # judge if timeout, go to low start
    if (timeout[rnd]):
        ssthresh = cwin_reno // 2
        cwin_reno = 1
        continue

    # if 3-redundant ACK received, go to quick re-trans
    if (retrans[rnd]):
        cwin_reno = ssthresh
        ssthresh = cwin_reno // 2

    # low start
    if (cwin_reno < ssthresh):
        cwin_reno *= 2
        if (cwin_reno > ssthresh):
            cwin_reno = ssthresh

    # congestion control
    elif (cwin_reno >= ssthresh): 
        cwin_reno += 1

# TCP Tahoe
for rnd in range(1,cnt):

    y2.append(cwin_tahoe)

    if (timeout[rnd]):
        th_tahoe = cwin_tahoe // 2
        cwin_tahoe = 1
        continue

    if (retrans[rnd]):
        th_tahoe = cwin_tahoe // 2
        cwin_tahoe = 1
        continue

    if (cwin_tahoe < th_tahoe):
        cwin_tahoe *= 2

        if (cwin_tahoe > th_tahoe):
            cwin_tahoe = th_tahoe

    elif (cwin_tahoe >= th_tahoe): 
        cwin_tahoe += 1

# plot the graph

plt.xlabel("传输回合")
plt.ylabel("拥塞窗口（以报文段记）")
plt.plot(trans_rnd, y1, 'r',label = 'TCP Reno')
plt.plot(trans_rnd, y2,'b',label = 'TCP Tahoe')
plt.grid()
plt.legend()
plt.show()