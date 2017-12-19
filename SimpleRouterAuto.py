#coding:utf-8
"""
This script automaticly create ned file and header for m port n tree fat tree topology
plid, swlid用两位表示一位
"""
import re
import glob
import numpy as np
import matplotlib.pyplot as plt
from optparse import OptionParser

class SimpleRouter(object):
    def __init__(self, port, delay, datarate, lane, packetsize, flitsize, bufferDepth, vc, routerDelay, injectionRate,
                 freq=0, traffic=0, hotspot=5):
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
        self.switch = 1
        self.port = port
        self.processor = port
        self.delay = delay  # ns
        self.lane = lane
        self.datarate = datarate * lane  # Gbps
        self.rawdatarate = datarate
        self.packetsize = packetsize # Byte
        self.flitsize = flitsize # Byte
        self.flitlength = packetsize / flitsize + 1 if packetsize % flitsize > 0 else packetsize / flitsize
        self.routerDelay = routerDelay * 1e-9 #ns
        self.bufferDepth = bufferDepth
        self.vc = vc
        self.injectionRate = injectionRate
        self.freq = self.datarate * 1.0e9 / (self.flitsize * 8) if freq == 0 else freq
        self.outBufferDepth = int(self.routerDelay * 1.0e-9 * self.freq) + 1 if self.routerDelay != 0 else 5
        self.simStartTime = 1  # start from 1.0s
        self.recordStartTime = self.simStartTime + self.routerDelay * 1.0e-9 * 1.2 + 0.0000006
        self.simEndTime = self.recordStartTime + 0.000002
        self.traffic = traffic
        self.hotspot = hotspot

    def printProcessorConnection(self):
        processorString = [""] * self.processor
        for i in range(self.processor):
            processorString[i] = "processor[" + str(i) +"].port <--> Channel <--> router[" + str(self.switch-1) + "].port_" + str(i) + ";"
        return processorString

    def printPortId(self):
        portString = [""] * self.port
        for i in range(self.port):
            portString[i] = "inout port_" + str(i) + ';'
            #print "inout port_%d;"%i
        return portString

    def createNed(self):
        nedfile = open("result/tianhe_router.ned", 'w')
        # write router
        nedfile.write("simple SimpleRouter\n")
        nedfile.write("{\n")
        nedfile.write("\tparameters:\n")
        nedfile.write("\n")
        nedfile.write("\tgates:\n")

        portstr = self.printPortId()
        for i in range(len(portstr)):
            nedfile.write("\t\t" + portstr[i] + "\n")

        nedfile.write("}\n")

        # write processor
        nedfile.write("simple SimpleProcessor\n")
        nedfile.write("{\n")
        nedfile.write("\tparameters:\n")
        nedfile.write("\n")
        nedfile.write("\tgates:\n")
        nedfile.write("\t\tinout port;\n")
        nedfile.write("}\n")

        # write topology
        nedfile.write("network Tianhe_Router\n")
        nedfile.write("{\n")
        nedfile.write("\ttypes:\n")
        nedfile.write("\t\tchannel Channel extends ned.DatarateChannel\n")
        nedfile.write("\t\t{\n")
        nedfile.write("\t\t\tdelay = " + str(self.delay) + "ns;\n")
        nedfile.write("\t\t\tdatarate = " + str(self.datarate) + "Gbps;\n")
        nedfile.write("\t\t}\n")
        nedfile.write("\tsubmodules:\n")
        nedfile.write("\t\trouter[" + str(self.switch) + "]: SimpleRouter {\n")
        nedfile.write("\n")
        nedfile.write("\t\t}\n")
        nedfile.write("\t\tprocessor[" + str(self.processor) + "]: SimpleProcessor{\n")
        nedfile.write("\n")
        nedfile.write("\t\t}\n")
        nedfile.write("\tconnections:\n")

        procstr = self.printProcessorConnection()
        for i in range(len(procstr)):
            nedfile.write("\t\t" + procstr[i] + "\n")

        nedfile.write("}\n")
        nedfile.close()

    def createHeader(self):
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
        headfile.write("#define CrossPointBufferDepth " + str(8) + '\n')
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

    def plotResult(self):
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
            packetDelayTimeTotal = 0
            packetDelayTimeCount = 0
            flitDropped = 0

            for line in lines:
                line = line.strip()
                list = re.split("  | |\t", line)
                # print list
                if len(list) == 11: # vector
                    nodetype, count, mean = list[6:9]
                    if nodetype == "flitDelayTime":
                        flitDelayTimeTotal += float(count) * float(mean)
                        flitDelayTimeCount += float(count)
                    elif nodetype == "hopCount":
                        hopCountTotal += float(count) * float(mean)
                        hopCountCount += float(count)
                    elif nodetype == "packageDelayTime":
                        packetDelayTimeTotal += float(count) * float(mean)
                        packetDelayTimeCount += float(count)
                elif len(list) == 8: # scalar
                    nodetype, value = list[6:8]
                    if nodetype == "timeCount":
                        timeCount = float(value)
                    elif nodetype == "flitReceived":
                        flitReceived += float(value)
                    elif nodetype == "flitSent":
                        flitSent += float(value)
                    elif nodetype == "packetDropped":
                        flitDropped += float(value) * self.flitlength


            txtfile.close()
            if flitDelayTimeCount != 0 and hopCountCount != 0:
                results.append([flitDelayTimeTotal / flitDelayTimeCount, hopCountTotal / hopCountCount, flitReceived, flitSent, flitDropped, timeCount])
        # each row in answers is a different simulation result
        # each column represent injectionRate, throughput, averageLatency
        # print "avg flit delay time\tavg hop count\tflit received\tflit sent\ttime count"
        # for result in results:
        #     print str(result[0]) + "\t" + str(result[1]) + "\t" + str(result[2]) + "\t" + str(result[3]) + "\t" + str(result[4])

        print "injectionRate\tthroughput\tavgFlitDelayTime\tBandwidth\tlane\tpacketSize\tflitSize\tbufferDepth\tvc"
        answers = []
        for result in results:
            # print result
            avgFlitDelayTime, avgHopCount, flitReceived, flitSent, flitDropped, timeCount = result
            injectionRate = 1.0 * (flitSent + flitDropped) / (timeCount * self.processor)
            # print str(flitSent) + " " + str(timeCount) + " " + str(self.processor)
            throughtput = 1.0 * flitReceived / (timeCount * self.processor)
            if injectionRate <= 1.0:
                answers.append([injectionRate, throughtput, avgFlitDelayTime + self.routerDelay])
            #加入routerDelay
            print str(injectionRate) + "\t" + str(throughtput) + "\t" + str(avgFlitDelayTime + self.routerDelay) \
            + "\t" + str(self.rawdatarate) + "\t" + str(self.lane) + "\t" + str(self.packetsize) \
            + "\t" + str(self.flitsize) + "\t" + str(self.bufferDepth) + "\t" + str(self.vc)


        rawData = np.array(answers)
        index = np.argsort(rawData, axis=0) # axis=0 means sorting the 0th dimension, and other dimension remain constant, that is sorting by column
        plotData = rawData[index[:,0],:] # sort according to first column
        # print plotData
        # print rawData

        figure = plt.figure(1, figsize=(16, 8))
        axe1 = figure.add_subplot(121)
        axe2 = figure.add_subplot(122)
        plt.sca(axe1)
        plt.plot(plotData[:,0], plotData[:,1], linewidth=2)
        plt.xlabel("Injection Rate")
        plt.ylabel("Throughput")
        plt.title("Router Bandwidth: " + str(self.datarate) + "Gbps * " + str(self.lane) + "lane")

        plt.sca(axe2)
        plt.plot(plotData[:,0], plotData[:,2], linewidth=2)
        plt.xlabel("Injection Rate")
        plt.ylabel("Average Flit Latency")
        plt.title("Injection Rate vs AverageLatency")
        # plt.legend()
        plt.show()

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
        headfile.write("sim-time-limit = " + str(self.simEndTime) + "s\n")

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

if __name__ == '__main__':

    tianhe_router = SimpleRouter(port=16, delay=5, datarate=14, lane=8, packetsize=16,
                                flitsize=4, bufferDepth=32, vc=3, routerDelay=1,injectionRate=float(option.injection_rate),
                                freq=float(option.freq), traffic=int(option.traffic), hotspot=float(option.hotspot))
    tianhe_router.createNed()
    tianhe_router.createHeader()
    tianhe_router.createINI()
    # tianhe_router.plotResult()