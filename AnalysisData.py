import re
import glob
import numpy as np
import sys
import matplotlib.pyplot as plt

def plotResult(self):
    """
    read file from log and calculate the flitDelayTime, HopCount, flitReceived, flitSent to get
    throughput, injection rate, latency
    :return:
    """
    file_list = ['baseline', 'highradix']  # different folder contains different data set
    dataSummary = []

    for i in range(len(file_list)):
        file_path = './data/' + str(file_list[i]) + '/*.sca'
        filenames = glob.glob(file_path)
        # each row is a different simulation result
        # each column represent avgFlitDelayTime, avgHopCount, flitReceived, flitSent, timeCount
        results = []

        for filename in filenames:
            txtfile = open(filename, 'r')
            lines = txtfile.readlines()
            # scalar variable for each file
            mydict = {
                'creditMsgDelayTimeCount' : 0,
                'creditMsgDelayTimeTotal' : 0,
                'flitByHop' : 0,
                'flitDelayTimeCount' : 0,
                'flitDelayTimeTotal' : 0,
                'flitReceived' : 0,
                'flitSent' : 0,
                'hopCountCount' : 0,
                'hopCountTotal' : 0,
                'packageReceived' : 0,
                'packageSent' : 0,
                'packetDelayTimeCount' : 0,
                'packetDelayTimeTotal' : 0,
                'packetDropped' : 0,
                'realMaxHandleMessagetime' : 0,
                'realMaxRouterTime' : 0,
                'realRouterTime' : 0,
                'realTotalHandleMessageTime' : 0,
                'realTotalTime' : 0,
                'routerPower' : 0,
                'timeCount' : 0
            }

            for line in lines:
                line = line.strip()
                list = re.split(" \t|  | |\t", line)
                # print list
                if len(list) == 4 and list[0] == 'scalar':
                    _, _, nodetype, value = list[:]
                    if nodetype == "flitDelayTimeTotal":
                        flitDelayTimeTotal += float(value)
                    if nodetype == "flitDelayTimeCount":
                        flitDelayTimeCount += float(value)
                    elif nodetype == "flitReceived":
                        flitReceived += float(value)
                    elif nodetype == "flitSent":
                        flitSent += float(value)
                    elif nodetype == "packetDelayTimeTotal":
                        packetDelayTimeTotal += float(value)
                    elif nodetype == "packetDelayTimeCount":
                        packetDelayTimeCount += float(value)
                    elif nodetype == "packetDropped":
                        packetDropped += float(value)
                    elif nodetype == "routerPower":
                        routerPower += routerPower
                    elif nodetype == "timeCount":
                        timeCount = float(value)

            txtfile.close()
            assert flitDelayTimeCount != 0 and packetDelayTimeCount != 0 and timeCount != 0

            results.append([flitDelayTimeTotal / flitDelayTimeCount, flitReceived, flitSent, packetDropped, timeCount])
        # each row in answers is a different simulation result
        # each column represent injectionRate, throughput, averageLatency
        answers = []
        for result in results:
            # print result
            avgFlitDelayTime, flitReceived, flitSent, packetDropped, timeCount = result
            # injectionRate = 1.0 * flitSent / (timeCount * self.processor)
            injectionRate = 1.0 * (flitSent + packetDropped * self.flitlength) / (timeCount * self.processor)
            throughtput = 1.0 * flitReceived / (timeCount * self.processor)
            answers.append([injectionRate, throughtput, avgFlitDelayTime])

        rawData = np.array(answers)
        index = np.argsort(rawData, axis=0) # axis=0 means sorting the 0th dimension, and other dimension remain constant, that is sorting by column
        plotData = rawData[index[:,0],:] # sort according to first column

        print plotData
        dataSummary.append(plotData)

    # print rawData

    figure = plt.figure(1, figsize=(16, 8))
    axe1 = figure.add_subplot(121)
    axe2 = figure.add_subplot(122)
    plt.sca(axe1)
    for i in range(len(file_list)):
        plt.scatter(dataSummary[i][:,0], dataSummary[i][:,1])
        plt.plot(dataSummary[i][:,0], dataSummary[i][:,1], linewidth=2)
    plt.xlabel("Injection Rate")
    plt.ylabel("Throughput")
    plt.title("Injection Rate vs Throughput")
    plt.legend([str(i) for i in file_list], loc='lower right')

    plt.sca(axe2)
    # plt.scatter(plotData[:,0], plotData[:,2])
    for i in range(len(file_list)):
        plt.plot(dataSummary[i][:,0], dataSummary[i][:,2] * 1.0e9, linewidth=2)
    plt.xlabel("Injection Rate")
    plt.ylabel("Average Latency / ns")
    plt.title("Injection Rate vs AverageLatency")

    plt.legend([str(i) for i in file_list])
    plt.show()