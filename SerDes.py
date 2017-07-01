#coding:utf-8
import re
import glob
import numpy as np
import matplotlib.pyplot as plt

total_tech_scale = []
total_channel_loss = [24, 21, 50, 18.4]
total_power = [602, 288, 403, 247.3]

tx_tech_scale = []
tx_channel_loss = [24, 21, 4.5, 7.5, 18.4, 6]
tx_power = [200, 152, 145, 97, 105.1, 120]

rx_tech_scale = []
rx_channel_loss = [24, 21, 23, 14.8, 40, 50, 18.4]
rx_power = [382, 136, 230, 102, 453, 320, 142.2]


tx_channel_loss_index = np.argsort(tx_channel_loss)
tx_channel_loss = np.array(tx_channel_loss)[tx_channel_loss_index]
tx_power = np.array(tx_power)[tx_channel_loss_index]

rx_channel_loss_index = np.argsort(rx_channel_loss)
rx_channel_loss = np.array(rx_channel_loss)[rx_channel_loss_index]
rx_power = np.array(rx_power)[rx_channel_loss_index]

tx_fit = np.polyfit(tx_channel_loss, tx_power, 1)
print tx_fit
tx = np.poly1d(tx_fit)
print tx
rx_fit = np.polyfit(rx_channel_loss, rx_power, 1)
print rx_fit
rx = np.poly1d(rx_fit)
print rx


figure = plt.figure(1, figsize=(16, 8))
axe1 = figure.add_subplot(121)
axe2 = figure.add_subplot(122)
# transceiver
plt.sca(axe1)
x = np.arange(0.0, 60, 0.01)
y = x * tx_fit[0] + tx_fit[1]
plt.plot(x, y, linewidth=2)
plt.scatter(tx_channel_loss, tx_power, marker='*', edgecolors='r')
plt.xlabel("Channel Loss/dB")
plt.ylabel("Power Dissipation/mW")
plt.title("Transmitter")

# receiver
plt.sca(axe2)
x = np.arange(0.0, 60, 0.01)
y = x * rx_fit[0] + rx_fit[1]
plt.plot(x, y, linewidth=2)
plt.scatter(rx_channel_loss, rx_power, marker='*', edgecolors='r')
plt.xlabel("Channel Loss/dB")
plt.ylabel("Power Dissipation/mW")
plt.title("Receiver")
plt.legend()
plt.show()
