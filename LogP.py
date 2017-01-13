"""
This is LogP module for parallel computing
"""
import numpy as np
import matplotlib.pyplot as plt
import math

class LogP(object):
    def __init__(self, latency, overhead, gap, processor, pointsTwoExpo, loadAndStore = 1):
        """
        All the parameters are scaled at micron meter
        """
        self.latency = latency
        self.overhead = overhead
        self.gap = gap
        self.processor = processor
        self.pointsArray = np.array([2 ** x for x in xrange(1, pointsTwoExpo + 1)])
        self.base = 2  # FFT base 2
        self.loadAndStore = loadAndStore
        self.comnicateTime = 0.0

    def calcComputaion(self):
        computeTime = 1.0 * self.pointsArray / self.processor * np.log(self.pointsArray) / np.log(self.base);
        return computeTime

    def calcCommunication(self):
        communicationTime = (1.0 * self.pointsArray / self.processor * max(self.loadAndStore + 2.0 * self.overhead, self.gap) + self.latency) \
                            * math.log(self.processor) / math.log(self.base)
        return communicationTime

    def plot(self):
        bandwidth = [1,2,3,5,7,10]
        latency = [3,6]
        communication = self.calcCommunication()
        computation = self.calcComputaion()
        figure = plt.figure(1, figsize=(16, 8))
        axe1 = figure.add_subplot(121)
        axe2 = figure.add_subplot(122)
        axe1.set_xscale("log")
        axe1.set_yscale("log")
        axe2.set_xscale("log")
        axe2.set_yscale("log")
        plt.sca(axe1)
        for band in bandwidth:
            self.gap = 20.0 / band
            self.latency = latency[0]
            communication = self.calcCommunication()
            plt.plot(self.pointsArray, communication, label = "bandwidth = %0.1dMB/s, latency = %0.1dus" % (band,latency[0]), linewidth=2)
        plt.xlabel("FFT points")
        plt.ylabel("Seconds")
        plt.legend()
        plt.sca(axe2)
        for band in bandwidth:
            self.gap = 20.0 / band
            self.latency = latency[1]
            communication = self.calcCommunication()
            plt.plot(self.pointsArray, communication, label = "bandwidth = %0.1dMB/s, latency = %0.1dus" % (band,latency[1]), linewidth=2)
        plt.xlabel("FFT points")
        plt.ylabel("Seconds")
        plt.legend()
        plt.show()


latency = 6
overhead = 2
gap = 4
pointsTwoExpo = 20
processor = 128
logp = LogP(latency, overhead, gap, processor, pointsTwoExpo)
logp.plot()