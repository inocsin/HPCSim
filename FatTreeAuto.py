#coding:utf-8
"""
This script automaticly create ned file and header for m port n tree Fat-Tree topology
plid, swlid用两位表示一位
linux版本，从sca文件中读取数据，omnet仿真结果只产生sca数据，不产生vec数据
"""
import re
import glob
import numpy as np
import sys
from optparse import OptionParser

class fatTree(object):

    def __init__(self, port, level, datarate,
                 lane, packetsize, flitsize,
                 bufferDepth, vc, crossPointBufferDepth,
                 routerDelay, injectionRate, traffic=0, hotspot=1,
                 freq=0, linkLatency=5*10, baseline=False):
        """
        :param port: number of ports
        :param level: the level of fat-tree
        :param delay: the delay of link in ns, 5ns/m
        :param datarate: the datarate of the link in Gbps
        :param packetsize: the packet size in Byte
        :param flitsize: the flit size in Byte
        :param routerDelay: router path-through latency in ns
        :param traffic: 0 for uniform, 1 for hotspot, 2 for transpose, 3 for complement, 4 for bitreversal
        :return:
        """
        self.port = port  # port number
        self.level = level  # level number n
        self.processor = 2 * (port / 2) ** level  # number of processor
        self.switch = (2 * level - 1) * (port / 2) ** (level - 1)  # switch number
        self.switchTop = (port / 2) ** (level - 1)  # number of switches in the top level
        self.switchLower = self.switch - self.switchTop  # number of lower switch
        self.switchLowerEach = self.switchLower / (self.level - 1)  # number of switches in each lower layer
        self.delay = linkLatency  # ns
        self.datarate = datarate * lane  # Gbps
        # self.rawDatarate = datarate  # Gbps
        self.packetsize = packetsize  # Byte
        self.flitsize = flitsize  # Byte
        self.flitlength = packetsize / flitsize + 1 if packetsize % flitsize > 0 else packetsize / flitsize
        self.bufferDepth = bufferDepth  # in packet
        self.crossPointBufferDepth = crossPointBufferDepth  # in flits
        self.vc = vc
        self.routerDelay = routerDelay  # in ns
        self.traffic = traffic
        if self.datarate == 0 and freq == 0:
            print("datarate and frequency cannot both equals 0")
            assert False
        self.freq = self.datarate * 1.0e9 / (self.flitsize * 8) if freq == 0 else freq
        self.simStartTime = 1  # start from 1.0s
        self.recordStartTime = self.simStartTime + self.routerDelay * 1.0e-9 * (2 * self.level - 1) * 1.2 + 0.0000006
        self.simEndTime = self.recordStartTime + 0.00002  # valid simulation time
        # denote the router path-trough latency
        self.outBufferDepth = int(self.routerDelay * 1.0e-9 * self.freq) + 1 if self.routerDelay != 0 else 3
        self.injectionRate = injectionRate
        self.baseline = False if baseline == 0 else True
        self.hotspot = hotspot

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
        nedfile = open("result/fat_tree.ned", 'w')
        # write router
        if self.baseline == True:
            nedfile.write("simple FtRouter\n")
        else:
            nedfile.write("simple HighRadixRouter\n")
        nedfile.write("{\n")
        nedfile.write("\tparameters:\n")
        nedfile.write("\n")
        nedfile.write("\tgates:\n")

        portstr = self.printPortId()
        for i in range(len(portstr)):
            nedfile.write("\t\t" + portstr[i] + "\n")

        nedfile.write("}\n")

        # write processor
        nedfile.write("simple FtProcessor\n")
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
        if self.delay != 0:
            nedfile.write("\t\t\tdelay = " + str(self.delay) + "ns;\n")
        if self.datarate != 0:
            nedfile.write("\t\t\tdatarate = " + str(self.datarate) + "Gbps;\n")
        nedfile.write("\t\t}\n")
        nedfile.write("\tsubmodules:\n")
        if self.baseline == True:
            nedfile.write("\t\trouter[" + str(self.switch) + "]: FtRouter {\n")
        else:
            nedfile.write("\t\trouter[" + str(self.switch) + "]: HighRadixRouter {\n")
        nedfile.write("\n")
        nedfile.write("\t\t}\n")
        nedfile.write("\t\tprocessor[" + str(self.processor) + "]: FtProcessor{\n")
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
        headfile = open("result/topoconfig.h", 'w')
        headfile.write("#ifndef TOPOCONFIG_H_TEMPLATE_\n")
        headfile.write("#define TOPOCONFIG_H_TEMPLATE_\n")
        headfile.write("//***********topology parameters***********\n")
        headfile.write("#define PortNum " + str(self.port) + "\n")
        headfile.write("#define ProcessorNum " + str(self.processor) + "\n")
        headfile.write("#define LinkNum " + str(self.switch * self.port + self.processor) + "\n")
        headfile.write("#define PacketSize " + str(self.packetsize) + "\n")
        headfile.write("#define FlitSize " + str(self.flitsize) + "\n")
        headfile.write("#define FlitLength " + str(self.flitlength) + "\n")
        headfile.write("#define VC " + str(self.vc) + "\n")
        headfile.write("#define BufferDepth " + str(self.bufferDepth) + " * FlitLength" + "\n")
        headfile.write("#define ProcessorBufferDepth " + str(self.bufferDepth) + " * FlitLength" + "\n")
        headfile.write("#define CrossPointBufferDepth " + str(self.crossPointBufferDepth) + '\n')
        headfile.write("#define FREQ " + str(self.freq) + "\n")
        headfile.write("#define OutBufferDepth " + str(self.outBufferDepth) + "\n")
        headfile.write("#define RecordStartTime " + str(self.recordStartTime) + '\n')
        headfile.write("//*************unchangable variable***************\n")
        headfile.write("#define CLK_CYCLE 1/FREQ\n")
        headfile.write("#define Sim_Start_Time 1\n")
        headfile.write("#define TimeScale 0.1\n")
        headfile.write("//*************injection mode***************\n")
        headfile.write("#define Traffic " + str(self.traffic) + "\n")
        headfile.write("#define Hotspot " + str(self.hotspot) + "\n")
        headfile.write("#define LAMBDA 7\n")
        headfile.write("#define INJECTION_RATE " + str(self.injectionRate) + "\n")
        headfile.write("//*************debug infomation***************\n")
        headfile.write("#define Verbose 1\n")
        headfile.write("#define VERBOSE_DEBUG_MESSAGES 1\n")
        headfile.write("#define VERBOSE_DETAIL_DEBUG_MESSAGES 2\n")
        headfile.write("//************power infomation***************\n")
        headfile.write("#define LVT 1\n")
        headfile.write("#define NVT 2\n")
        headfile.write("#define HVT 3\n")
        headfile.write("#define VDD 1.0\n")
        headfile.write("#define PARM(x) PARM_ ## x\n")
        headfile.write("#define PARM_TECH_POINT 45\n")
        headfile.write("#define PARM_TRANSISTOR_TYPE NVT\n")
        headfile.write("#define FlitWidth FlitSize * 8\n")
        headfile.write("//***********end of parameter definition*****\n")
        headfile.write("#endif /* TOPOCONFIG_H_TEMPLATE_ */")

        # create fat_tree.h
        headfile = open("result/fat_tree_topo.h", 'w')
        headfile.write("#ifndef FAT_TREE_TOPO_H_\n")
        headfile.write("#define FAT_TREE_TOPO_H_\n")
        headfile.write("#define LevelNum " + str(self.level) + "\n")
        headfile.write("#define SwitchNum " + str(self.switch) + "\n")
        headfile.write("#define SwTop " + str(self.switchTop) + "\n")
        headfile.write("#define SwLower " + str(self.switchLower) + "\n")
        headfile.write("#define SwLowEach " + str(self.switchLowerEach) + "\n")
        headfile.write("#endif /* FAT_TREE_TOPO_H_ */\n")
        headfile.close()

    def createINI(self):
        # create omnetpp.ini
        headfile = open("result/omnetpp.ini", 'w')
        headfile.write("[General]\n")
        headfile.write("\n")
        headfile.write("[Config FatTree]\n")
        headfile.write("network = Fat_tree\n")
        headfile.write("sim-time-limit = " + str(self.simEndTime) + "s\n")
        headfile.write("\n")
        headfile.write("[Config TianheRouter]\n")
        headfile.write("network = Tianhe_Router\n")
        headfile.write("sim-time-limit = 1.000100s\n")

        headfile.close()

# define parser
parser = OptionParser()
parser.add_option("-i", "--injection_rate", dest="injection_rate", help="Injection Rate")
parser.add_option("-p", "--pass_through_latency", dest="pass_through_latency", help="Pass Through Latency in ns")
parser.add_option("-l", "--link_latency", dest="link_latency", help="Link Latency in ns")
parser.add_option("-b", "--baseline", dest="baseline", help="Baseline router")
parser.add_option("-u", "--buffer", dest="buffer", help="Input buffer depth")
parser.add_option("-d", "--datarate", dest="datarate", help="Datarate per lane in Gbps")
parser.add_option("-f", "--freq", dest="freq", help="Frequency")
parser.add_option("-t", "--traffic", dest="traffic", help="Traffic Pattern")
parser.add_option("-s", "--hotspot", dest="hotspot", help="Hotspot percentage")

option, args = parser.parse_args()

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


# main function
if __name__ == '__main__':
    # fattree = fatTree(port=16, level=3, datarate=14,
    #               lane=8, packetsize=128, flitsize=4,
    #               bufferDepth=4, vc=3, crossPointBufferDepth=8,
    #               routerDelay=float(option.pass_through_latency),
    #               injectionRate=float(option.injection_rate), linkLatency=float(option.link_latency))

    fattree = fatTree(port=4, level=3, datarate=float(option.datarate),
              lane=1, packetsize=16, flitsize=4,
              bufferDepth=int(option.buffer), vc=3, crossPointBufferDepth=8,
              routerDelay=float(option.pass_through_latency),
              freq=float(option.freq), traffic=int(option.traffic), hotspot=float(option.hotspot),
              injectionRate=float(option.injection_rate), linkLatency=float(option.link_latency),
              baseline=int(option.baseline))
    # print option.injection_rate
    # print option.pass_through_latency

    # print sys.argv
    fattree.createNed()
    fattree.createHeader()
    fattree.createINI()