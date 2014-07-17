import matplotlib.pyplot as plt
import csv
import numpy as np
from pylab import *
import scipy as sp
from scipy.stats import *
import copy
import file_tools as ft
import random
import sys

def plot_scatter_plot_of_errors(file_name):
	"""
	this function is for plotting the errors detected vs errors inserted.
	Usually file name is final.csv
	"""
	data = ft.get_data_from_file(file_name)

	x, y = get_list_of_data_as_x_and_y(data)

	plt.ylabel("number of detected errors")
	plt.xlabel("number of induced errors")
	plt.title("Correlation among induced errors and detected errors")
	plt.scatter(x, y, marker=",")
	plt.show()

def get_list_of_data_as_x_and_y(data):
	x = []
	y = []

	for row in data:
		x.append(row[0]) #the time
		y.append(row[1]) #the type

	return x,y

def set_font_of_plot():
	font = {"family" : "Century Gothic",
			"size"   : 22}

	matplotlib.rc("font", **font)

def show_scatter_plot_of_data(x, y, plot_title, x_label, y_label, alpha = 0.5):
	plt.ylabel(y_label)
	plt.xlabel(x_label)
	plt.title(plot_title)
	plt.scatter(x, y, alpha = 0.5)
	plt.show()

def plot_number_of_sensors_that_deviate_and_is_rare_event(file_name):
	"""
	Plots the number of sensors that deviate and are rare event from the file.
	usually the file name is number_of_sensors_that_deviate_and_is_rare_event.csv.
	"""
	def add_wiggle(ys, amount):
		return [y + random.random() * amount for y in ys]

	def count_quadrants(x, y, x_threshold, y_threshold):
		true_positives = false_positives = true_negatives = false_negatives = 0
		for x, y in zip(x, y):
			if x < x_threshold and y < y_threshold:
				true_negatives += 1
			elif x < x_threshold and y > y_threshold:
				false_negatives += 1
			elif x > x_threshold and y < y_threshold:
				false_positives += 1
			else:
				true_positives += 1

		print "True negatives:", true_negatives
		print "True positives:", true_positives
		print "False negatives:", false_negatives
		print "False positives:", false_positives

	def change_from_boolean_string_to_integer(list_of_boolean_string_values):
		"Returns a list containing 1 for True and 0 for False"
		return [1 if val == 'True' else 0 for val in list_of_boolean_string_values]

	warmup_time = 1500
	data = ft.get_data_from_file(file_name)
	data = data[warmup_time:]
	x , y = get_list_of_data_as_x_and_y(data)
	x = [int(i) for i in x]
	y = change_from_boolean_string_to_integer(y)

	count_quadrants(x, y, 0.5, 0.5)
	
	y = add_wiggle(y, 0.1)


	plt.axhline(0.5, xmin = 0, xmax =100, color="r")
	plt.axvline(0.5, ymin = 0, ymax =1, color="r")

	show_scatter_plot_of_data(x, y, "Anomalies vs no anomalies", "Number of deviating sensors", "Is rare event?")

def plot_error_if_greater_than_zero(file_name):

	def is_greater_than_zero(list_of_values):
		return [1 if int(val) > 0 else 0 for val in list_of_values]

	data = ft.get_data_from_file(file_name)
	y, _ = get_list_of_data_as_x_and_y(data)

	warmup_time = 1500
	x = range(warmup_time, len(y) + warmup_time)
	y = is_greater_than_zero(y)

	show_scatter_plot_of_data(x, y, "Anomalies vs no anomalies", "Time", "Is rare event?")

def plot_time_series_file(file_name, title = "", ylabel = "", xlabel = ""):
	data = ft.get_data_from_file(file_name)
	transposed_data = map(list, zip(*data))
	set_font_of_plot()
	plt.ylabel(ylabel)
	plt.xlabel(xlabel)
	plt.title(title)
	plt.plot(transposed_data)
	plt.show()

def plot_file_in_columns(file_name):
	data = ft.get_data_from_file(file_name)
	plt.plot(data)
	plt.show()

def plot_false_and_true_positives(positive_file_name, false_file_name):
	positive_data = ft.get_data_from_file(positive_file_name)
	false_data = ft.get_data_from_file(false_file_name)

	positive_x, positive_y = get_list_of_data_as_x_and_y(positive_data)
	false_x, false_y = get_list_of_data_as_x_and_y(false_data)

	plt.plot(positive_x, positive_y, "b-", false_x, false_y, "ro")
	plt.show()

def show_menu():
	print \
	"1 - Scatther plot of errors. \n" + \
	"2 - Scatter plot of sensors that deviate and is rare event.\n" + \
	"3 - Plot any time series file. \n" + \
	"4 - Plot file that is in columns\n" + \
	"5 - Plot if greater than zero\n" + \
	"6 - Plot true vs false positives\n" + \
	"0 - Exit"
	print "Which choice do you want to show?:",

	choice = int(input())
	if choice == 0:
		return
	else:
		if choice < 6:
			print "Enter the file name:",
			file_name = raw_input()

			if choice == 1:
				plot_scatter_plot_of_errors(file_name)

			if choice == 2:
				plot_number_of_sensors_that_deviate_and_is_rare_event(file_name)

			if choice == 3:
				print "Do you want to add labels? yes/no:",
				do_ask_for_labels = raw_input()

				if do_ask_for_labels == 'yes':
					print "Enter title:",
					title = raw_input()
					print "Enter y label:",
					ylabel = raw_input()
					print "Enter x label:",
					xlabel = raw_input()
					plot_time_series_file(file_name, title, ylabel, xlabel)
				else:
					plot_time_series_file(file_name)

			if choice == 4:
				plot_file_in_columns(file_name)

			if choice == 5:
				plot_error_if_greater_than_zero(file_name)
		else:
			if choice == 6:
				print "Enter positive file name:",
				positive_file_name = raw_input()
				print "Enter false file name:",
				false_file_name = raw_input()

				plot_false_and_true_positives(positive_file_name, false_file_name)


def main():
	show_menu()

if __name__ == "__main__":
	main()


