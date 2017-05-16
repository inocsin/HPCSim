"""
This is LogP module for parallel computing
"""
import numpy as np
import matplotlib.pyplot as plt
import math

class LogP(object):
    def __init__(self, **kwargs):
        """
        All the parameters are scaled at micron meter
        """
        self.tsend = kwargs.pop('tsend', 0) # send time of processor
        self.treceive = kwargs.pop('treceive', 0) # receive time of processor
        self.overhead = kwargs.pop('overhead', 0)
        self.procFreq = kwargs.pop('procFreq', 1e9) # floating point compution frequency

        if self.overhead == 0: # processor overhead
            self.overhead = (self.tsend + self.treceive) / 2

        self.latency = kwargs.pop('latency', 0) # the total latency of transfer message in the link
        self.msgSize = kwargs.pop('msgSize', 32) # message size
        self.bandwidth = kwargs.pop('bandwidth', 10e9) # bandwidth of link
        self.avgRouter = kwargs.pop('avgRouter', 9.3) # average hop of router
        self.routerDelay = kwargs.pop('routerDelay', 1e-6)
        self.linkLatency = kwargs.pop('linkLatency', 20 / (2e8))
        self.linkOverhead = kwargs.pop('linkOverhead', 0)

        if self.latency == 0:
            self.latency = self.avgRouter * (self.routerDelay + self.linkLatency + self.linkOverhead * 2) + self.msgSize / self.bandwidth

        self.gap0 = kwargs.pop('gap', 0) # the original gap = 1 / (saturation_rate * max_inject_freq)
        self.gap = max(self.gap0, self.msgSize / self.bandwidth)
        self.processor = kwargs.pop('processor', 1024)
        self.pointsTwoExpo = kwargs.pop('pointsTwoExpo', 10)
        self.pointsArray = np.array([2 ** x for x in xrange(1, self.pointsTwoExpo + 1)])
        self.loadAndStore = kwargs.pop('loadAndStore',0) # store and load data

        # debug
        # print "gap=" + str(self.gap)
        # print "latency=" + str(self.latency)

    def updateValue(self):
        # update values
        self.overhead = (self.tsend + self.treceive) / 2
        self.latency = self.avgRouter * (self.routerDelay + self.linkLatency + self.linkOverhead  * 2) + self.msgSize / self.bandwidth
        self.gap = max(self.gap0, self.msgSize / self.bandwidth)

    def calcComputaion(self):
        pass

    def calcCommunication(self):
        pass

    def oprationTime(self):
        pass

    def plot(self, name):
        pass



class FFT(LogP):
    def __init__(self, **kwargs):
        super(FFT,self).__init__(**kwargs)
        self.base = 2  # FFT base 2

    def calcComputaion(self):
        computeTime = 1.0 * self.pointsArray / self.processor * np.log(self.pointsArray) / np.log(self.base) / self.procFreq
        return computeTime

    def calcCommunication(self):
        pass

    def oprationTime(self):
        # calculate the time cost per operation in average
        self.updateValue()
        opTime = (self.calcCommunication() + self.calcComputaion()) / (self.pointsArray * np.log(self.pointsArray) / np.log(self.base))
        return opTime

    def plot(self, name):
        bandwidth = np.array([0.1,0.5,1,5,10]) * 1e9
        # latency = [3,6]
        figure = plt.figure(1, figsize=(8, 8))
        axe1 = figure.add_subplot(111)
        axe2 = figure.add_subplot(111)
        axe1.set_xscale("log")
        axe1.set_yscale("log")
        axe2.set_xscale("log")
        axe2.set_yscale("log")
        plt.sca(axe1)
        for band in bandwidth:
            self.bandwidth = band
            opTime = self.oprationTime()
            opTime_us = opTime * 1e6
            plt.plot(self.pointsArray, opTime_us, label = "bandwidth = %4.2fGbps" % (1.0 * band / 1e9), linewidth=2)
        plt.xlabel("FFT Points")
        plt.ylabel("Per FFT Operation/us")
        plt.title(name)
        plt.legend()
        # plt.sca(axe2)
        # for band in bandwidth:
        #     self.gap = 20.0 / band
        #     self.latency = latency[1]
        #     communication = self.calcCommunication()
        #     plt.plot(self.pointsArray, communication, label = "bandwidth = %0.1dMB/s, latency = %0.1dus" % (band,latency[1]), linewidth=2)
        # plt.xlabel("FFT points")
        # plt.ylabel("Seconds")
        # plt.legend()
        plt.show()


class cyclicFFT(FFT):
    def __init__(self, **kwargs):
        super(cyclicFFT,self).__init__(**kwargs)

    def calcCommunication(self):
        communicationTime = (1.0 * self.pointsArray / self.processor * max(self.loadAndStore + 2.0 * self.overhead, self.gap) + self.latency) \
                            * math.log(self.processor) / math.log(self.base)
        return communicationTime

    def plot(self, name):
        super(cyclicFFT,self).plot(name)

    def myplot(self):
        self.plot("Cyclic Layout")


class hybridFFT(FFT):
    def __init__(self, **kwargs):
        super(hybridFFT,self).__init__(**kwargs)

    def calcCommunication(self):
        communicationTime = (1.0 * self.pointsArray * (1 / self.processor - 1 / self.processor ** 2) * max(self.loadAndStore + 2.0 * self.overhead, self.gap) + self.latency)
        return communicationTime

    def plot(self, name):
        super(hybridFFT,self).plot(name)

    def myplot(self):
        self.plot("Hybrid Layout")

class LU(LogP):
    def __init__(self, **kwargs):
        super(LU,self).__init__(**kwargs)

    def calcComputaion(self):
        computeTime = np.zeros(self.pointsArray.shape)
        for n in xrange(1, self.pointsTwoExpo + 1):
            N = 2 ** n
            for k in xrange(0,N-1):
                computeTime[n-1] = computeTime[n-1] + 2 * (N - k) ** 2 / self.processor
        computeTime = computeTime * self.procFreq
        return computeTime

    def calcCommunication(self):
        pass

    def oprationTime(self):
        opration = np.array([2.0 / 3.0 * x ** 3 + 2.0 * x ** 2 for x in self.pointsArray])
        opTime = (self.calcCommunication() + self.calcComputaion()) / opration
        return opTime

    def plot(self, name):
        bandwidth = np.array([0.1,0.5,1,5,10]) * 1e9
        # latency = [3,6]
        figure = plt.figure(1, figsize=(8, 8))
        axe1 = figure.add_subplot(111)
        axe2 = figure.add_subplot(111)
        axe1.set_xscale("log")
        axe1.set_yscale("log")
        axe2.set_xscale("log")
        axe2.set_yscale("log")
        plt.sca(axe1)
        for band in bandwidth:
            self.bandwidth = band
            opTime = self.oprationTime()
            opTimeUS = opTime * 1e3
            plt.plot(self.pointsArray, opTimeUS, label = "bandwidth = %4.2fGbps" % (1.0 * band / 1e9), linewidth=2)
        plt.xlabel("Matirx Size N")
        plt.ylabel("Per Floating-point Operation/us")
        plt.title(name)
        plt.legend()
        # plt.sca(axe2)
        # for band in bandwidth:
        #     self.gap = 20.0 / band
        #     self.latency = latency[1]
        #     communication = self.calcCommunication()
        #     plt.plot(self.pointsArray, communication, label = "bandwidth = %0.1dMB/s, latency = %0.1dus" % (band,latency[1]), linewidth=2)
        # plt.xlabel("FFT points")
        # plt.ylabel("Seconds")
        # plt.legend()
        plt.show()

class randomLU(LU):
    def __init__(self, **kwargs):
        super(randomLU,self).__init__(**kwargs)

    def calcCommunication(self):
        communicationTime = np.zeros(self.pointsArray.shape)
        for n in xrange(1, self.pointsTwoExpo + 1):
            N = 2 ** n
            for k in xrange(1,N-1):
                communicationTime[n-1] = communicationTime[n-1] + 2 * (N - k) * max(self.loadAndStore + 2.0 * self.overhead, self.gap) + self.latency
        return communicationTime

    def plot(self, name):
        super(randomLU,self).plot(name)

    def myplot(self):
        self.plot("Random Layout")


class columnLU(LU):
    def __init__(self, **kwargs):
        super(columnLU,self).__init__(**kwargs)

    def calcCommunication(self):
        communicationTime = np.zeros(self.pointsArray.shape)
        for n in xrange(1, self.pointsTwoExpo + 1):
            N = 2 ** n
            for k in xrange(1,N-1):
                communicationTime[n-1] = communicationTime[n-1] + (N - k) * max(self.loadAndStore + 2.0 * self.overhead, self.gap) + self.latency
        return communicationTime

    def plot(self, name):
        super(columnLU,self).plot(name)

    def myplot(self):
        self.plot("Column Layout")




# logp = logP(procFreq =, tsend = , treceive = , [overhead =], msgSize = , bandwidth = , avgRouter = ,
#             routerDelay = , linkLatency = , linkOverhead =, [latency =], gap = ,processor =,
#             prointsTwoExpo = , loadAndStore =)

# dawn 6000

print "================begin cyclicFFT================"
cyclic = cyclicFFT(procFreq = 1.5e8, tsend = 66e-9, treceive = 66e-9, msgSize = 128, bandwidth = 10e9, avgRouter = 4.3,
                    routerDelay = 38.4e-9, linkLatency = 20/(3e8), linkOverhead = 0, gap = 1 / 312.5e6, processor = 1024,
                    prointsTwoExpo = 30, loadAndStore =0)
print cyclic.calcCommunication()
print cyclic.calcComputaion()
print cyclic.oprationTime()
cyclic.myplot()

print "================begin hybridFFT================"
hybrid = hybridFFT(procFreq = 1.5e8, tsend = 66e-9, treceive = 66e-9, msgSize = 128, bandwidth = 10e9, avgRouter = 4.3,
                    routerDelay = 38.4e-9, linkLatency = 20/(3e8), linkOverhead = 0, gap = 1 / 312.5e6, processor = 1024,
                    prointsTwoExpo = 30, loadAndStore =0)
print hybrid.calcCommunication()
print hybrid.calcComputaion()
print hybrid.oprationTime()
hybrid.myplot()

print "================begin randomLU================"
randomlu = randomLU(procFreq = 1.5e8, tsend = 66e-9, treceive = 66e-9, msgSize = 128, bandwidth = 10e9, avgRouter = 4.3,
                    routerDelay = 38.4e-9, linkLatency = 20/(3e8), linkOverhead = 0, gap = 1 / 312.5e6, processor = 1024,
                    prointsTwoExpo = 30, loadAndStore =0)
print randomlu.calcCommunication()
print randomlu.calcComputaion()
print randomlu.oprationTime()
randomlu.myplot()

print "================begin columnLU================"
columnlu = columnLU(procFreq = 1.5e8, tsend = 66e-9, treceive = 66e-9, msgSize = 128, bandwidth = 10e9, avgRouter = 4.3,
                    routerDelay = 38.4e-9, linkLatency = 20/(3e8), linkOverhead = 0, gap = 1 / 312.5e6, processor = 1024,
                    prointsTwoExpo = 30, loadAndStore =0)
print columnlu.calcCommunication()
print columnlu.calcComputaion()
print columnlu.oprationTime()
columnlu.myplot()
