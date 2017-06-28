#coding:utf-8
import re
import glob
import numpy as np
import matplotlib.pyplot as plt

channel_loss_total = [24, 21, 50, 18.4]
channel_loss_tx = [24, 21, 4.5, 7.5, 18.4, 6]
channel_loss_rx = [24, 21, 23, 14.8, 40, 50, 18.4]

tx_power = [200, 152, 145, 97, 105.1, 120]
rx_power = [382, 136, 230, 102, 453, 320, 142.2]
total_power = [602, 288, 403, 247.3]

channel_loss_tx_index = np.argsort(channel_loss_tx)
channel_loss_tx = np.array(channel_loss_tx)[channel_loss_tx_index]
tx_power = np.array(tx_power)[channel_loss_tx_index]

channel_loss_rx_index = np.argsort(channel_loss_rx)
channel_loss_rx = np.array(channel_loss_rx)[channel_loss_rx_index]
rx_power = np.array(rx_power)[channel_loss_rx_index]

tx_fit = np.polyfit(channel_loss_tx, tx_power, 1)
print tx_fit
# p1 = np.poly1d(tx_fit)
# print p1
rx_fit = np.polyfit(channel_loss_rx, rx_power, 1)
print rx_fit

figure = plt.figure(1, figsize=(16, 8))
axe1 = figure.add_subplot(121)
axe2 = figure.add_subplot(122)
plt.sca(axe1)
# tx
x = np.arange(0.0, 60, 0.01)
y = x * tx_fit[0] + tx_fit[1]
plt.plot(x, y, linewidth=2)
plt.scatter(channel_loss_tx, tx_power, marker='*', edgecolors='r')
plt.xlabel("Channel Loss/dB")
plt.ylabel("Power Dissipation/mW")
plt.title("Transceiver")

plt.sca(axe2)
x = np.arange(0.0, 60, 0.01)

y = x * rx_fit[0] + rx_fit[1]
plt.plot(x, y, linewidth=2)
plt.scatter(channel_loss_rx, rx_power, marker='*', edgecolors='r')
plt.xlabel("Channel Loss/dB")
plt.ylabel("Power Dissipation/mW")
plt.title("Receiver")
plt.legend()
plt.show()
