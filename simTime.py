#coding:utf-8
import re
import glob

def analysisTimeCost():
    filenames = glob.glob('log/simtime.txt')
    filecount = 0
    print "file\tflitSent\tflitReceived\tclockCount\tmaxRouterTime\tmaxHandleMsgTime\trouterTime\thandleMsgTime\trealTime\trouterTime/realTime"
    for filename in filenames:
        filecount += 1
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
        packetReceived = 0
        packetSent = 0
        packetDropped = 0
        realMaxHandleMessagetime = 0
        realMaxRouterTime = 0
        realRouterTime = 0
        realTotalHandleMessageTime = 0
        realTotalTime = 0

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
            elif len(list) == 8: # scalar
                nodetype, value = list[6:8]
                if nodetype == "timeCount":
                    timeCount = float(value) # 以时钟周期计算
                elif nodetype == "flitReceived":
                    flitReceived += float(value)
                elif nodetype == "flitSent":
                    flitSent += float(value)
                elif nodetype == "packageReceived":
                    packetReceived += float(value)
                elif nodetype == "packageSent":
                    packetSent += float(value)
                elif nodetype == "packetDropped":
                    packetDropped += float(value)
                elif nodetype == "realMaxHandleMessagetime":
                    if float(value) > realMaxHandleMessagetime:
                        realMaxHandleMessagetime = float(value)
                elif nodetype == "realMaxRouterTime":
                    if float(value) > realMaxRouterTime:
                        realMaxRouterTime = float(value)
                elif nodetype == "realRouterTime":
                    realRouterTime += float(value)
                elif nodetype == "realTotalHandleMessageTime":
                    realTotalHandleMessageTime += float(value)
                elif nodetype == "realTotalTime":
                    realTotalTime = float(value)

        txtfile.close()
        if realTotalTime > 0:
            print str(filecount) + "\t" + str(flitSent) + "\t" + str(flitReceived) + "\t" + str(timeCount) + \
                  "\t" + str(realMaxRouterTime) + "\t" + str(realMaxHandleMessagetime) + "\t" + \
                str(realRouterTime) + "\t" + str(realTotalHandleMessageTime) + "\t" + str(realTotalTime) + "\t" + \
                str(1.0 * realRouterTime / realTotalTime)

analysisTimeCost()

