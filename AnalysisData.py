import re
import glob
import numpy as np
import sys
import os
import matplotlib.pyplot as plt

marker = ['.', ',', 'o', 'v', '^', '<', '>', '1', '2', '3', '4', 's', 'p', '*', 'h', 'H', '+', 'x', 'D', 'd', '|', '_']

def preprocessData(nparray, axis, flag=True, method='slope'):
    """
    To make sure that the latency doesn't fall
    Data format: injection rate, throughput, latency
    :param nparray:
    :param axis:
    :param flag: True means use the method
    :param method: 'slope' or 'increase'
    :return:
    """
    assert isinstance(nparray, np.ndarray)
    shape = nparray.shape
    assert len(shape) == 2 and shape[1] == 3
    assert axis > 0 and axis < shape[1]
    index = -1
    for i in range(2, shape[0]):
        if method == 'slope':
            slope2 = (nparray[i,axis] - nparray[i-1,axis]) / (nparray[i,0] - nparray[i-1,0])
            slope1 = (nparray[i-1,axis] - nparray[i-2,axis]) / (nparray[i-1,0] - nparray[i-2,0])
            if slope2 < slope1:
                index = i
                break
        else:
            if nparray[i,axis] < nparray[i-1,axis]:
                index = i
                break

    if index == -1 or flag == False:
        return nparray
    else:
        return nparray[:index, :]


def plotResult():
    """
    read file from log and calculate the flitDelayTime, HopCount, flitReceived, flitSent to get
    throughput, injection rate, latency
    :return:
    """

    # different folder contains different data set
    file_list = []
    dataSummary = []  # 3 dimension data, 0 for curve, 1 for different injection rate data set, 2 for injection rate, throughput and latency
    for fpath, dirs, fs in os.walk('./data'):
        print fpath, dirs, fs
        file_list.extend(dirs)
        if 'backup' in file_list:
            file_list.remove('backup')  # remove backup file
        break


    # different curve
    for i in range(len(file_list)):
        print("In file: " + file_list[i])
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
                        # print("Not support nodetype: " + str(nodetype))
                        pass


            txtfile.close()
            assert mydict['flitDelayTimeCount'] != 0 and mydict['timeCount'] != 0
            results.append([mydict['flitDelayTimeTotal'] / mydict['flitDelayTimeCount'],
                            mydict['flitReceived'], mydict['flitSent'], mydict['packetDropped'],
                            mydict['processorNum'], mydict['flitLength'], mydict['timeCount']])
        # each row in answers is a different simulation result
        # each column represent injectionRate, throughput, averageLatency

        for result in results:
            # print result
            avgFlitDelayTime, flitReceived, flitSent, packetDropped, processorNum, flitLength, timeCount = result
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
    plt.xlim(0.0, 1.05)
    plt.ylim(0.0, 1.05)
    for i in range(len(file_list)):
        plotData = preprocessData(dataSummary[i], 1, False, 'increase')
        plt.scatter(plotData[:,0], plotData[:,1])
        plt.plot(plotData[:,0], plotData[:,1], marker[i]+'-', linewidth=1)
    plt.xlabel("Injection Rate")
    plt.ylabel("Throughput")
    plt.title("Injection Rate vs Throughput")
    plt.legend([str(i) for i in file_list], loc='upper left')

    plt.sca(axe2)
    # plt.scatter(plotData[:,0], plotData[:,2])
    plt.xlim(0.0, 1.05)
    # plt.ylim(0.0, 200)
    for i in range(len(file_list)):
        plotData = preprocessData(dataSummary[i], 2, False, 'increase')
        plt.scatter(plotData[:,0], plotData[:,2] * 1.0e9)
        plt.plot(plotData[:,0], plotData[:,2] * 1.0e9, marker[i]+'-', linewidth=1)
    plt.xlabel("Injection Rate")
    plt.ylabel("Latency / ns")
    plt.title("Injection Rate vs Latency")
    plt.legend([str(i) for i in file_list], loc='upper left')

    plt.show()

plotResult()