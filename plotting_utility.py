import matplotlib.pyplot as plt
import csv
import numpy as np
from pylab import *
import scipy as sp
from scipy.stats import *
import copy
import file_tools as ft

def plot_scatter_plot_of_errors():
	data = ft.get_data_from_file("final.csv")

	x, y = get_list_of_data_as_x_and_y(data)

	plt.ylabel("# of anomalies")
	plt.xlabel("# of induced errors")
	plt.title("Correlation among induced errors and detected errors")
	plt.scatter(x, y)
	plt.show()

def get_list_of_data_as_x_and_y(data):
	x = []
	y = []

	for row in data:
		x.append(row[0]) #the time
		y.append(row[1]) #the type

	return x,y

def show_scatter_plot_of_data(x, y, plot_title, x_label, y_label, alpha = 0.5):
	plt.ylabel(y_label)
	plt.xlabel(x_label)
	plt.title(plot_title)
	plt.scatter(x, y, alpha = 0.5)
	plt.show()

def plot_number_of_sensors_that_deviate_and_is_rare_event():
	"Plots the number of sensors that deviate and are rare event from the file."

	def change_from_boolean_string_to_integer(list_of_boolean_string_values):
		"Returns a list containing 1 for True and 0 for False"
		return [1 if val == 'True' else 0 for val in list_of_boolean_string_values]

	data = ft.get_data_from_file("number_of_sensors_that_deviate_and_is_rare_event.csv")
	_ , y = get_list_of_data_as_x_and_y(data)

	warmup_time = 1500
	x = range(warmup_time, len(y) + warmup_time)
	y = change_from_boolean_string_to_integer(y)

	show_scatter_plot_of_data(x, y, "Anomalies vs no anomalies", "Time", "Is rare event?")

def plot_time_series_file(file_name):
	data = ft.get_data_from_file(file_name)
	transposed_data = map(list, zip(*data))
	plt.plot(transposed_data)
	plt.show()

#plot_number_of_sensors_that_deviate_and_is_rare_event()
#plot_time_series_file("sensors_after_rare_event.csv")
plot_time_series_file("sensors_before_rare_event.csv")


