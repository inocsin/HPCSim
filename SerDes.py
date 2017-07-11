#coding:utf-8
import re
import glob
import numpy as np
import matplotlib.pyplot as plt

# total_tech_scale = []
# total_voltage = []
# total_channel_loss = [24, 21, 50, 18.4]
# total_power = [602, 288, 403, 247.3]

tx_tech_scale = [40, 65, 28, 14, 28, 28, 16, 28, 14]
# tx_voltage_supply = [1.5, ]
# tx_output_voltage =
tx_datarate = [28, 60, 64, 56, 56, 45, 64, 36, 28]
tx_channel_loss = [24, 21, 4.5, 7.5, 18.4, 6, 6, 11, 13]
tx_power = [200, 152, 145, 97, 105.1, 120, 225, 84, 195]
tx_paper_index = [1, 2, 4, 5, 11, 12, 13, 17, 18]

rx_tech_scale = [40, 65, 16, 28, 32, 28, 28, 65]
# rx_voltage_supply = [1, ]
# rx_receive_voltage = []
rx_datarate = [28, 60, 40, 32, 25.6, 32, 56, 10]
rx_channel_loss = [24, 21, 23, 14.8, 40, 56, 18.4, 25.3]
rx_power = [382, 136, 230, 102, 453, 320, 142.2, 87]
rx_paper_index = [1, 2, 3, 6, 7, 8, 11, 19]

# sort the data
tx_channel_loss_index = np.argsort(tx_channel_loss)
tx_channel_loss = np.array(tx_channel_loss)[tx_channel_loss_index]
tx_tech_scale = np.array(tx_tech_scale)[tx_channel_loss_index]
tx_datarate = np.array(tx_datarate)[tx_channel_loss_index]
tx_power = np.array(tx_power)[tx_channel_loss_index]
tx_paper_index = np.array(tx_paper_index)[tx_channel_loss_index]

rx_channel_loss_index = np.argsort(rx_channel_loss)
rx_channel_loss = np.array(rx_channel_loss)[rx_channel_loss_index]
rx_tech_scale = np.array(rx_tech_scale)[rx_channel_loss_index]
rx_datarate = np.array(rx_datarate)[rx_channel_loss_index]
rx_power = np.array(rx_power)[rx_channel_loss_index]
rx_paper_index = np.array(rx_paper_index)[rx_channel_loss_index]


# figure 1 power vs channel loss
tx_fit = np.polyfit(tx_channel_loss, tx_power, 1)
print tx_fit
tx = np.poly1d(tx_fit)
print tx
rx_fit = np.polyfit(rx_channel_loss, rx_power, 1)
print rx_fit
rx = np.poly1d(rx_fit)
print rx

figure1 = plt.figure(1, figsize=(16, 8))
axe1 = figure1.add_subplot(121)
axe2 = figure1.add_subplot(122)
# transmitter
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

# figure 2 power with scale vs channel loss
tx_power_scale = tx_power * 1.0 / (tx_tech_scale ** 2)
tx_fit = np.polyfit(tx_channel_loss, tx_power_scale, 1)
rx_power_scale = rx_power * 1.0 / (rx_tech_scale ** 2)
rx_fit = np.polyfit(rx_channel_loss, rx_power_scale, 1)

figure2 = plt.figure(2, figsize=(16, 8))
axe1 = figure2.add_subplot(121)
axe2 = figure2.add_subplot(122)
# transmitter
plt.sca(axe1)
x = np.arange(0.0, 60, 0.01)
y = x * tx_fit[0] + tx_fit[1]
plt.plot(x, y, linewidth=2)
plt.scatter(tx_channel_loss, tx_power_scale, marker='*', edgecolors='r')
plt.xlabel("Channel Loss [dB]")
plt.ylabel("Power Dissipation with Scaling [mW/nm2]")
plt.title("Transmitter")

# receiver
plt.sca(axe2)
x = np.arange(0.0, 60, 0.01)
y = x * rx_fit[0] + rx_fit[1]
plt.plot(x, y, linewidth=2)
plt.scatter(rx_channel_loss, rx_power_scale, marker='*', edgecolors='r')
plt.xlabel("Channel Loss [dB]")
plt.ylabel("Power Dissipation [mW/nm2]")
plt.title("Receiver")
plt.legend()
plt.show()

# figure 3 Power Efficiency vs channel loss
tx_power_efficiency = tx_power * 1.0 / tx_datarate
tx_fit = np.polyfit(tx_channel_loss, tx_power_efficiency, 1)
rx_power_efficiency = rx_power * 1.0 / rx_datarate
rx_fit = np.polyfit(rx_channel_loss, rx_power_efficiency, 1)

figure3 = plt.figure(3, figsize=(16, 8))
axe1 = figure3.add_subplot(121)
axe2 = figure3.add_subplot(122)
# transmitter
plt.sca(axe1)
x = np.arange(0.0, 60, 0.01)
y = x * tx_fit[0] + tx_fit[1]
plt.plot(x, y, linewidth=2)
plt.scatter(tx_channel_loss, tx_power_efficiency, marker='.', edgecolors='r')
for i in range(len(tx_paper_index)):
    plt.annotate('['+str(tx_paper_index[i])+']',
                 xy=(tx_channel_loss[i], tx_power_efficiency[i]),
                 xytext=(tx_channel_loss[i], tx_power_efficiency[i]))
plt.xlabel("Channel Loss [dB]")
plt.ylabel("Power Efficiency [mW/Gb/s]")
plt.title("Transmitter")

# receiver
plt.sca(axe2)
x = np.arange(0.0, 60, 0.01)
y = x * rx_fit[0] + rx_fit[1]
plt.plot(x, y, linewidth=2)
plt.scatter(rx_channel_loss, rx_power_efficiency, marker='.', edgecolors='r')
for i in range(len(rx_paper_index)):
    plt.annotate('['+str(rx_paper_index[i])+']',
                 xy=(rx_channel_loss[i], rx_power_efficiency[i]),
                 xytext=(rx_channel_loss[i], rx_power_efficiency[i]))
plt.xlabel("Channel Loss [dB]")
plt.ylabel("Power Efficiency [mW/Gb/s]")
plt.title("Receiver")
plt.legend()
plt.show()