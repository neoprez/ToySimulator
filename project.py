"""
This is the project
"""
import random
import csv
import station as st
import matplotlib.pyplot as plt
import numpy as np

#random generator, uses seeds for testing purposes if you want repeatability
random_generator = random.Random(1) 
#error parameters
probability_of_erroneous_reading = 0.05
erroneous_reading_standard_deviation = 20
number_of_continous_erroneous_readings = 5

#sensor parameters
number_of_sensors_per_station = 1
number_of_readings = 10
actual_temperature = 20
sensor_standard_deviation = 2
station_standard_deviation = 2
global_temperature = 20
list_of_station_shifts = [10, -7, 2]

def save_data_to_file(data, file_name):
	with open(file_name, 'wb') as csv_file:
		csv_writer = csv.writer(csv_file)
		for time_series in data:
			csv_writer.writerow(time_series)

def generate_error_free_data(hub, number_of_readings):
	"Generates error free data from each station"
	#get reading from all sensors in station
	def get_data_from_station(stat):
		return stat.get_reading_from_all_sensors_in_station(number_of_readings)

	dataset = []

	for stat in hub:
		data_from_sensors = get_data_from_station(hub[stat])
		for sens in data_from_sensors:
			for read in sens:
				dataset.append(read)
	return dataset

def add_erroneous_readings_to_data(data, probability_of_erroneous_reading, 
	erroneous_reading_standard_deviation, random_generator):
	def get_erroneous_value(value):
		return random_generator.normalvariate(value, erroneous_reading_standard_deviation)

	def get_value_with_probabilistics_erroneous_value(value):
		if random_generator.random() < probability_of_erroneous_reading:
			return get_erroneous_value(value)
		return value

	return [[get_value_with_probabilistics_erroneous_value(value) for value in time_series] 
		for time_series in data]

def add_erroneous_continuous_sequence_to_data(data, probability_of_erroneous_reading, 
	number_of_continous_erroneous_readings, random_generator):
	"""
	This function produces a continous sequence of erroneous readings. 
	Ex: 34, 35,35,35, 32, 38 ...
	"""
	def does_continous_erroneous_value_starts():
		return random_generator.random() < probability_of_erroneous_reading

	def add_index_repeat_value(time_series, start_index):
		end_index = min(start_index+number_of_continous_erroneous_readings, 
			len(time_series))
		for i in range(start_index, end_index):
			time_series[i] = time_series[start_index]

		return time_series

	revised_data = []

	for time_series in data:
		modified_time_series = time_series[:]
		for index in range(len(modified_time_series)):
			if does_continous_erroneous_value_starts():
				#repeat the sequence
				modified_time_series = add_index_repeat_value(modified_time_series, index)
		revised_data.append(modified_time_series)
	
	return revised_data

def plot_station(stat, data, plt):
	def create_a_list_for_each_data_point_in_station():
		" This method returns the number of figures contained in the dataset "
		return [[] for _ in range(stat.get_number_of_sensors())]

	def sort_values_by_sensor(data_points):
		for r in data:
			idx = ord(r[0]) - 65 #gets the value of the sensor to be used as index
			data_points[idx].append([r[1], r[2]])
		return data_points

	def get_x_and_y_for_each_data_point(data_points):
		x_and_y_for_each_data_point = []
		#after the data from each figure has beeing organized, this proceeds to create
		#an orgranized list containing the x, y values for each data figure
		for idx in range(len(data_points)):
			x1 = []
			y1 = []
			for data in data_points[idx]:
				x1.append(data[0])
				y1.append(data[1])
			x_and_y_for_each_data_point.append(x1)
			x_and_y_for_each_data_point.append(y1)
		return x_and_y_for_each_data_point

	list_of_data_points = create_a_list_for_each_data_point_in_station()
	data_points = sort_values_by_sensor(list_of_data_points)
	x_and_y_for_each_data_point = get_x_and_y_for_each_data_point(data_points)

	#figure = plt.figure()
	#axes = figure.add_subplot(3,1,(i+1)) #width x height by figure number
	for i in range(0, len(data_points) * 2, 2):
		plt.plot(x_and_y_for_each_data_point[i], x_and_y_for_each_data_point[i+1])
	
	plt.grid()

def main():
	station_names = ["A", "B", "C"] #name of the stations
	main_hub = {} #creates a dictionary to keep stations

	#create an station
	station_a = st.Station(global_temperature + list_of_station_shifts[0], 
		station_standard_deviation, station_names[0], random_generator)

	#add multople sensors to station
	station_a.add_sensor_to_station("A", sensor_standard_deviation)
	station_a.add_sensor_to_station("B", sensor_standard_deviation)
	station_a.add_sensor_to_station("C", sensor_standard_deviation)
	station_a.add_sensor_to_station("D", sensor_standard_deviation)
	station_a.add_sensor_to_station("E", sensor_standard_deviation)

	#connect sensors so that they are able to send data through each other
	#station_a.connect_sensors("E", "D")
	#station_a.connect_sensors("E", "C")
	#station_a.connect_sensors("D", "B")
	#station_a.connect_sensors("D", "C")
	#station_a.connect_sensors("B", "A")
	#station_a.connect_sensors("C", "A")

	station_b = st.Station(global_temperature + list_of_station_shifts[1], 
		station_standard_deviation, station_names[1], random_generator)

	station_b.add_sensor_to_station("A", sensor_standard_deviation)
	station_b.add_sensor_to_station("B", sensor_standard_deviation)
	station_b.add_sensor_to_station("C", sensor_standard_deviation)
	station_b.add_sensor_to_station("D", sensor_standard_deviation)
	station_b.add_sensor_to_station("E", sensor_standard_deviation)

	station_b.connect_sensors("E", "D")
	station_b.connect_sensors("E", "C")
	station_b.connect_sensors("D", "B")
	station_b.connect_sensors("C", "B")
	station_b.connect_sensors("C", "A")
	station_b.connect_sensors("B", "A")

	station_c = st.Station(global_temperature + list_of_station_shifts[2], 
		station_standard_deviation, station_names[2], random_generator)

	station_c.add_sensor_to_station("A", sensor_standard_deviation)
	station_c.add_sensor_to_station("B", sensor_standard_deviation)
	station_c.add_sensor_to_station("C", sensor_standard_deviation)
	station_c.add_sensor_to_station("D", sensor_standard_deviation)
	station_c.add_sensor_to_station("E", sensor_standard_deviation)

	station_c.connect_sensors("E", "C")
	station_c.connect_sensors("D", "E")
	station_c.connect_sensors("D", "C")
	station_c.connect_sensors("C", "B")
	station_c.connect_sensors("C", "A")
	station_c.connect_sensors("B", "A")

	main_hub[station_names[0]] = station_a
	#main_hub[station_names[1]] = station_b
	#main_hub[station_names[2]] = station_c

	data = generate_error_free_data(main_hub, number_of_readings)
	save_data_to_file(data, "data.csv")

	data_figures = []	#to keep the data figures in case I want to edit in the future
	figure = plt.figure() #to plot each data in different figures

	dataset = [["Sensor id", "Time", "Reading"]]



	data_label = [] #to hold the labels of each sensor
	
	plot_station(station_a, data, plt)

	plt.show()







	save_data_to_file(data_figures, "d.csv")
	#for r in range(len(data)):
	#	for c in range(len(data[r])):

	#	axes = figure.add_subplot(3,1,(i+1)) #width x height by figure number
	#	axes.set_title("data " + str(i))

	#	axes.plot(data[i])
	#	data_figures.append(axes)
	
	#plt.plot(x_and_y_for_each_data_figure)
	
	#plt.legend()


main()