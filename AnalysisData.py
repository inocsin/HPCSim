import re
import glob
import numpy as np
import sys
import matplotlib.pyplot as plt

def plotResult():
    """
    read file from log and calculate the flitDelayTime, HopCount, flitReceived, flitSent to get
    throughput, injection rate, latency
    :return:
    """
    file_list = ['baseline', 'highradix']  # different folder contains different data set
    dataSummary = []  # 3 dimension data, 0 for curve, 1 for different injection rate data set, 2 for injection rate, throughput and latency

    # different curve
    for i in range(len(file_list)):
        file_path = './data/' + str(file_list[i]) + '/*.sca'
        filenames = glob.glob(file_path)
        # each row is a different simulation result
        # each column represent avgFlitDelayTime, avgHopCount, flitReceived, flitSent, timeCount
        results = []  # store sum value
        answers = []  # store injection rate, throughput, latency
        # different injection rate
        for filename in filenames:
            # scalar variable for each file
            mydict = {
                # 'creditMsgDelayTimeCount' : 0,
                # 'creditMsgDelayTimeTotal' : 0,
                # 'flitByHop' : 0,
                'flitDelayTimeCount' : 0,
                'flitDelayTimeTotal' : 0,
                'flitReceived' : 0,
                'flitSent' : 0,
                # 'hopCountCount' : 0,
                # 'hopCountTotal' : 0,
                # 'packageReceived' : 0,
                # 'packageSent' : 0,
                # 'packetDelayTimeCount' : 0,
                # 'packetDelayTimeTotal' : 0,
                'packetDropped' : 0,
                # 'realMaxHandleMessagetime' : 0,
                # 'realMaxRouterTime' : 0,
                # 'realRouterTime' : 0,
                # 'realTotalHandleMessageTime' : 0,
                # 'realTotalTime' : 0,
                # 'routerPower' : 0,
                'processorNum': 0,
                'flitLength': 0,
                'timeCount': 0
            }
            txtfile = open(filename, 'r')
            lines = txtfile.readlines()
            for line in lines:
                line = line.strip()
                list = re.split(" \t|  | |\t", line)
                # print list
                if len(list) == 4 and list[0] == 'scalar':
                    _, _, nodetype, value = list[:]
                    if nodetype in mydict:
                        mydict[nodetype] += float(value)
                    else:
                        print("Not support nodetype: " + str(nodetype))


            txtfile.close()
            assert mydict['flitDelayTimeCount'] != 0 and mydict['timeCount'] != 0
            results.append([mydict['flitDelayTimeTotal'] / mydict['flitDelayTimeCount'],
                            mydict['flitReceived'], mydict['flitSent'], mydict['packetDropped'],
                            mydict['processorNum'], mydict['flitLength'], mydict['timeCount']])
        # each row in answers is a different simulation result
        # each column represent injectionRate, throughput, averageLatency

        for result in results:
            # print result
            avgFlitDelayTime, flitReceived, flitSent, packetDropped, timeCount, processorNum, flitLength = result
            # injectionRate = 1.0 * flitSent / (timeCount * self.processor)
            injectionRate = 1.0 * (flitSent + packetDropped * flitLength) / (timeCount * processorNum)
            throughtput = 1.0 * flitReceived / (timeCount * processorNum)
            answers.append([injectionRate, throughtput, avgFlitDelayTime])

        rawData = np.array(answers)
        index = np.argsort(rawData, axis=0)  # axis=0 means sorting the 0th dimension, and other dimension remain constant, that is sorting by column
        plotData = rawData[index[:,0],:]  # sort according to first column

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
        plt.scatter(dataSummary[i][:,0], dataSummary[i][:,2] * 1.0e9)
        plt.plot(dataSummary[i][:,0], dataSummary[i][:,2] * 1.0e9, linewidth=2)
    plt.xlabel("Injection Rate")
    plt.ylabel("Latency / ns")
    plt.title("Injection Rate vs Latency")

    plt.legend([str(i) for i in file_list])
    plt.show()

plotResult()