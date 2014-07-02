import matplotlib.pyplot as plt
import csv
import numpy as np
from pylab import *
import scipy as sp
from scipy.stats import *

def get_data_from_file(file_name, mode="rb"):
	data = []
	with open(file_name, mode) as csv_file:
		csv_reader = csv.reader(csv_file)
		for row in csv_reader:
			data.append(row)
	return data

def plot_scatter_plot_of_errors():
	data = get_data_from_file("final.csv")

	x = np.array(data[0])
	y = np.array(data[1])

	plt.ylabel("# of anomalies")
	plt.xlabel("# of induced errors")
	plt.title("Correlation among induced errors and detected errors")
	plt.scatter(x, y)
	plt.show()

def plot_scatter_plot_of_errors_vs_anomalies_detected():
	data = get_data_from_file("binary_list_of_sensors_.csv")
	x = []
	y = []

	for row in data:
		x.append(row[0])
		y.append(row[1])

	x = np.array(x)
	y = np.array(y)

	plt.ylabel("Is anomaly?")
	plt.xlabel("# of Sensors reporting erroneous readings")
	plt.title("Correlation anomalies vs errors")
	plt.scatter(x, y, alpha = 0.5)
	plt.show()

plot_scatter_plot_of_errors_vs_anomalies_detected()