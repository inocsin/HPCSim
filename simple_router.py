#coding:utf-8
"""
This script automaticly create ned file and header for m port n tree fat tree topology
plid, swlid用两位表示一位
"""
import re
import glob
import numpy as np
import matplotlib.pyplot as plt

class SimpleRouter(object):
    def __init__(self, port, delay, datarate, lane, packetsize, flitsize, bufferDepth, vc, routerDelay):
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
        # create fat_tree.h
        headfile = open("result/tianhe_router.h", 'w')
        headfile.write("#define PortNum " + str(self.port) + "\n")
        headfile.write("#define ProcessorNum " + str(self.processor) + "\n")
        headfile.write("#define PacketSize " + str(self.packetsize) + "\n")
        headfile.write("#define FlitSize " + str(self.flitsize) + "\n")
        headfile.write("#define FlitLength " + str(self.flitlength) + "\n")
        headfile.write("#define VC " + str(self.vc) + "\n")
        headfile.write("#define BufferDepth " + str(self.bufferDepth) + " * FlitLength" + "\n")
        headfile.write("#define ProcessorBufferDepth " + str(self.bufferDepth) + " * FlitLength" + "\n")
        headfile.write("#define FREQ " + str(self.datarate * 1.0e9 / (self.flitsize * 8)) + "\n")
        headfile.write("#define OutBufferDepth " + str(int(self.routerDelay * 1.0e9 / self.datarate * self.flitsize * 8) + 1) + "\n")

        headfile.close()


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


#port, delay, datarate, lane, packetsize, flitsize, bufferDepth, vc, routerDelay
tianhe_router = SimpleRouter(24, 0, 14, 8, 128, 4, 4, 3, 100)
tianhe_router.createNed()
tianhe_router.createHeader()
tianhe_router.plotResult()