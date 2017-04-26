#coding:utf-8
"""
This script automaticly create ned file and header for m port n tree fat tree topology
plid, swlid用两位表示一位
"""
import re
import glob
import numpy as np
import matplotlib.pyplot as plt

class fatTree(object):

    def __init__(self, port, level, delay, datarate, packetsize, flitsize):
        """

        :param port: number of ports
        :param level: the level of fat-tree
        :param delay: the delay of link in ns, 5ns/m
        :param datarate: the datarate of the link in Gbps
        :param packetsize: the packet size in Byte
        :param flitsize: the flit size in Byte
        :return:
        """
        self.port = port  # port number
        self.level = level  # level number n
        self.processor = 2 * (port / 2) ** level  # number of processor
        self.switch = (2 * level - 1) * (port / 2) ** (level - 1)  # switch number
        self.switchTop = (port / 2) ** (level - 1)  # number of switches in the top level
        self.switchLower = self.switch - self.switchTop  # number of lower switch
        self.switchLowerEach = self.switchLower / (self.level - 1)  # number of switches in each lower layer
        self.delay = delay  # ns
        self.datarate = datarate  # Gbps
        self.packetsize = packetsize # Byte
        self.flitsize = flitsize # Byte
        self.flitlength = packetsize / flitsize + 1 if packetsize % flitsize > 0 else packetsize / flitsize

    def debugPrint(self):
        print "********************** this is debug message ******************************"
        print "port number = %d, level number = %d, processor node = %d, switch count = %d"%(self.port, self.level, self.processor, self.switch)

    def ppid2plid(self, ppid):
        idtmp = ppid
        idfinal = 0
        mul = 1
        # mul每次乘以100，用两位表示一位，如15_7_7表示为150707
        for j in range(self.level-1):
            idfinal = idfinal + idtmp % (self.port / 2) * mul
            mul = mul * 100
            idtmp = (int) (idtmp / (self.port / 2))
        idfinal = idfinal + idtmp * mul
        return idfinal

    def plid2ppid(self, plid):
        tmp = plid
        mul = 1
        IDtmp = 0
        for j in range(self.level):
            IDtmp = IDtmp + mul * (tmp % 100)
            mul = mul * (self.port / 2)
            tmp = tmp / 100
        return IDtmp

    def swpid2swlid(self, swpid):
        # 首先判断i在哪一层
        level = 0
        find_level = False
        for j in range(self.level - 1):
            if swpid >= j * self.switchLowerEach and swpid < (j + 1) * self.switchLowerEach:
                level = j
                find_level = True
                break
        if not find_level:
            level = self.level - 1
        # 已经找到switch所在层，接下来对其进行编码
        # 先对非顶层的switch进行编码
        if level < self.level - 1:
            tmp = swpid - level * self.switchLowerEach
            IDtmp = 0
            mul = 1
            for j in range(self.level - 2):
                IDtmp = mul * (tmp % (self.port / 2)) + IDtmp
                tmp = (int) (tmp / (self.port / 2))
                mul = mul * 100
            IDtmp = IDtmp + mul * tmp
            mul = mul * 100
            IDtmp = mul * level + IDtmp  # 最前面加上它的层数
            return IDtmp
        # 接下来对顶层的switch进行操作
        else:
            tmp = swpid
            IDtmp = 0
            mul = 1
            for j in range(self.level-1):
                IDtmp = mul * (tmp % (self.port / 2)) + IDtmp
                tmp = (int) (tmp / (self.port / 2))
                mul = mul * 100
            IDtmp = mul * level + IDtmp
            return IDtmp

    def swlid2swpid(self, swlid):
        tmp = swlid
        level = tmp / (100 ** (self.level - 1))
        tmp = tmp % (100 ** (self.level - 1))
        IDtmp = level * self.switchLowerEach
        mul = 1
        for j in range(self.level-1):
            IDtmp = IDtmp + mul * (tmp % 100)
            mul = mul * (self.port / 2)
            tmp = tmp / 100
        return IDtmp

    def printPortId(self):
        portString = [""] * self.port
        for i in range(self.port):
            portString[i] = "inout port_" + str(i) + ';'
            #print "inout port_%d;"%i
        return portString

    def printProcessorConnection(self):
        processorString = [""] * self.processor
        for i in range(self.processor):
            ppid = i
            plid = self.ppid2plid(ppid)
            l = 0
            c = plid / 100
            k = plid % 100
            swlid = l * (10 ** ((self.level - 1) * 2)) + c
            swpid = self.swlid2swpid(swlid)
            #print swlid,swpid
            #print "processor[%d].port <--> Channel <--> router[%d].port_%d;"%(ppid, swpid, k)
            processorString[i] = "processor[" + str(ppid) +"].port <--> Channel <--> router[" + str(swpid) + "].port_" + str(k) + ";"
        return processorString

    def printSwitchConnection(self):
        # 每一个switch只负责向上的连接
        switchString = []
        for i in range(self.switch-self.switchTop):
            swpid = i
            swlid = self.swpid2swlid(swpid)
            l = swlid / (10 ** ((self.level - 1) * 2))
            l2 = l + 1
            #print swpid,swlid,l,l2
            c = swlid % (10 ** ((self.level - 1) * 2))
            k2 = (c / (10 ** (l * 2))) % 100
            #print c,k2
            for j in range(self.port / 2, self.port):
                k = j
                cl2 = k - self.port / 2
                #print k,cl2
                c2 = c % (10 ** (l * 2)) + cl2 * (10 ** (l * 2)) + c / (10 ** ((l + 1) * 2)) * (10 ** ((l + 1) * 2))
                swlid2 = l2 * (10 ** ((self.level - 1) * 2)) + c2
                swpid2 = self.swlid2swpid(swlid2)
                #print "swpid:%d, swlid:%d, port:%d --> swpid2:%d, swlid2:%d, port:%d"%(swpid,swlid,k,swpid2,swlid2,k2)
                #print "router[%d].port_%d <--> Channel <--> router[%d].port_%d;"%(swpid, k, swpid2, k2)
                switchString.append("router[" + str(swpid) + "].port_" + str(k) + " <--> Channel <--> router[" + str(swpid2) + "].port_" + str(k2) + ";")
        return switchString



    def createNed(self):
        nedfile = open("fat_tree.ned", 'w')
        # write router
        nedfile.write("simple Router\n")
        nedfile.write("{\n")
        nedfile.write("\tparameters:\n")
        nedfile.write("\n")
        nedfile.write("\tgates:\n")

        portstr = self.printPortId()
        for i in range(len(portstr)):
            nedfile.write("\t\t" + portstr[i] + "\n")

        nedfile.write("}\n")

        # write processor
        nedfile.write("simple Processor\n")
        nedfile.write("{\n")
        nedfile.write("\tparameters:\n")
        nedfile.write("\n")
        nedfile.write("\tgates:\n")
        nedfile.write("\t\tinout port;\n")
        nedfile.write("}\n")


        # writre fat_tree
        nedfile.write("network Fat_tree\n")
        nedfile.write("{\n")
        nedfile.write("\ttypes:\n")
        nedfile.write("\t\tchannel Channel extends ned.DatarateChannel\n")
        nedfile.write("\t\t{\n")
        nedfile.write("\t\t\tdelay = " + str(self.delay) + "ns;\n")
        nedfile.write("\t\t\tdatarate = " + str(self.datarate) + "Gbps;\n")
        nedfile.write("\t\t}\n")
        nedfile.write("\tsubmodules:\n")
        nedfile.write("\t\trouter[" + str(self.switch) + "]: Router {\n")
        nedfile.write("\n")
        nedfile.write("\t\t}\n")
        nedfile.write("\t\tprocessor[" + str(self.processor) + "]: Processor{\n")
        nedfile.write("\n")
        nedfile.write("\t\t}\n")
        nedfile.write("\tconnections:\n")

        procstr = self.printProcessorConnection()
        for i in range(len(procstr)):
            nedfile.write("\t\t" + procstr[i] + "\n")

        switchstr = self.printSwitchConnection()
        for i in range(len(switchstr)):
            nedfile.write("\t\t" + switchstr[i] + "\n")

        nedfile.write("}\n")

        nedfile.close()
    def createHeader(self):
        # create fat_tree.h
        headfile = open("fat_tree.h", 'w')
        headfile.write("#define PortNum " + str(self.port) + "\n")
        headfile.write("#define LevelNum " + str(self.level) + "\n")
        headfile.write("#define ProcessorNum " + str(self.processor) + "\n")
        headfile.write("#define SwitchNum " + str(self.switch) + "\n")
        headfile.write("#define LinkNum " + str(self.switch * self.port + self.processor) + "\n")
        headfile.write("#define SwTop " + str(self.switchTop) + "\n")
        headfile.write("#define SwLower " + str(self.switchLower) + "\n")
        headfile.write("#define SwLowEach " + str(self.switchLowerEach) + "\n")
        headfile.write("#define PacketSize " + str(self.packetsize) + "\n")
        headfile.write("#define FlitSize " + str(self.flitsize) + "\n")
        headfile.write("#define FlitLength " + str(self.flitlength) + "\n")

        headfile.close()

    def plotResult(self):
        """
        read file from log and calculate the flitDelayTime, HopCount, flitReceived, flitSent to get
        throughput, injection rate, latency
        :return:
        """
        filenames = glob.glob('./log/*.txt')
        # each row is a different simulation result
        # each column represent avgFlitDelayTime, avgHopCount, flitReceived, flitSent, timeCount
        results = []

        for filename in filenames:
            txtfile = open(filename, 'r')
            lines = txtfile.readlines()
            # tmp variable for each file
            flitDelayTimeTotal = 0
            flitDelayTimeCount = 0
            hopCountTotal = 0
            hopCountCount = 0
            flitReceived = 0
            flitSent = 0
            timeCount = 0

            for line in lines:
                line = line.strip()
                list = re.split("  | |\t", line)
                # print list
                if len(list) == 11:
                    nodetype, count, mean = list[6:9]
                    if nodetype == "flitDelayTime":
                        flitDelayTimeTotal += float(count) * float(mean)
                        flitDelayTimeCount += float(count)
                    elif nodetype == "hopCount":
                        hopCountTotal += float(count) * float(mean)
                        hopCountCount += float(count)
                elif len(list) == 8:
                    nodetype, value = list[6:9]
                    if nodetype == "timeCount":
                        timeCount = float(value)
                    elif nodetype == "flitReceived":
                        flitReceived += float(value)
                    elif nodetype == "flitSent":
                        flitSent += float(value)
            txtfile.close()
            if flitDelayTimeCount != 0 and hopCountCount != 0:
                results.append([flitDelayTimeTotal / flitDelayTimeCount, hopCountTotal / hopCountCount, flitReceived, flitSent, timeCount])
        # each row in answers is a different simulation result
        # each column represent injectionRate, throughput, averageLatency
        answers = []
        for result in results:
            # print result
            avgFlitDelayTime, avgHopCount, flitReceived, flitSent, timeCount = result
            injectionRate = 1.0 * flitSent / (timeCount * self.processor)
            throughtput = 1.0 * flitReceived / (timeCount * self.processor)
            answers.append([injectionRate, throughtput, avgFlitDelayTime])

        rawData = np.array(answers)
        index = np.argsort(rawData, axis=0) # axis=0 means sorting the 0th dimension, and other dimension remain constant, that is sorting by column
        plotData = rawData[index[:,0],:] # sort according to first column
        print plotData
        # print rawData

        figure = plt.figure(1, figsize=(16, 8))
        axe1 = figure.add_subplot(121)
        axe2 = figure.add_subplot(122)
        plt.sca(axe1)
        plt.plot(plotData[:,0], plotData[:,1], linewidth=2)
        plt.xlabel("Injection Rate")
        plt.ylabel("Throughput")
        plt.title("Injection Rate vs Throughput")

        plt.sca(axe2)
        plt.plot(plotData[:,0], plotData[:,2], linewidth=2)
        plt.xlabel("Injection Rate")
        plt.ylabel("Average Latency")
        plt.title("Injection Rate vs AverageLatency")
        # plt.legend()
        plt.show()







# main function
# port, level, delay, datarate, packetsize, flitsize
fattree = fatTree(16,3,1,100,1000,200)
# print fattree.swpid2swlid(319)
# print fattree.swlid2swpid(20707)
# print fattree.swpid2swlid(255)
# print fattree.swlid2swpid(11507)
# print fattree.swpid2swlid(127)
# print fattree.swlid2swpid(1507)
# print fattree.swpid2swlid(128)
# print fattree.swlid2swpid(10000)
# print "processor"
# print fattree.ppid2plid(1023)
# print fattree.plid2ppid(150707)

fattree.createNed()
fattree.createHeader()

# fattree.plotResult()