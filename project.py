"""
This is the project
"""
import random
import csv
import station as st
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time as time
import copy

def save_data_to_file(data, file_name):
	with open(file_name, 'wb') as csv_file:
		csv_writer = csv.writer(csv_file)
		for time_series in data:
			csv_writer.writerow(time_series)

def generate_error_free_data(stat, number_of_readings):
	"Generates error free data from a station"
	#get reading from all sensors in station
	def get_data_from_station():
		return stat.get_reading_from_all_sensors_in_station(number_of_readings)

	dataset = []

	data_from_sensors = get_data_from_station()
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

	erroneous_data = []
	for data_point in data:
		erroneous_value = get_value_with_probabilistics_erroneous_value(data_point[2])
		erroneous_data.append([data_point[0], data_point[1], erroneous_value])
	
	return erroneous_data

def add_erroneous_continuous_sequence_to_data(data, probability_of_erroneous_reading, 
	number_of_continous_erroneous_readings, random_generator):
	"""
	This function produces a continous sequence of erroneous readings. 
	Ex: 34, 35,35,35, 32, 38 ...
	"""
	def does_continous_erroneous_value_starts():
		return random_generator.random() < probability_of_erroneous_reading

	def add_index_repeat_value(modified_data, row):
		""" Inserts sequence to modified data """
		start_row = row
		end_row = min(start_row+number_of_continous_erroneous_readings, len(modified_data))
		
		data_from_actual_row = modified_data[row]
		continous_value = data_from_actual_row[2]

		for r in range(start_row, end_row):
			data_from_actual_row = modified_data[r]
			data_from_actual_row[2] = continous_value

	modified_data = copy.deepcopy(data)

	for row in range(len(modified_data)):
		if does_continous_erroneous_value_starts():
			add_index_repeat_value(modified_data, row)

	return modified_data

def plot_station(stat, data, figure_numb, width, height, title, figure):
	def create_a_list_for_each_data_point_in_station():
		" This method returns the number of figures contained in the dataset "
		return [[] for _ in range(stat.get_number_of_sensors())]

	def sort_values_by_sensor(data_points):
		for r in data:
			idx = r[0] - 1 #gets the value of the sensor to be used as index
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

	axes = figure.add_subplot(height,width, figure_numb) # height x width by figure number
	for i in range(0, len(data_points) * 2, 2):
		axes.plot(x_and_y_for_each_data_point[i], x_and_y_for_each_data_point[i+1])
		axes.set_title(title)
		axes.set_xlabel("Time")
		axes.set_ylabel("Reading")
	
	axes.grid()

def read_data_over_time(main_hub, number_of_readings, oscilation_time, width, height):
	"""
	This function shows a plot of every station reading over time.
	Oscilation time in seconds.
	"""
	plt.ion() #activates interactive mode, so that another line can be run after the plot is shown
	figures_in_graph_count = 0
	figure = plt.figure()

	current_number_of_readings = 0
	while current_number_of_readings < number_of_readings:
		current_number_of_readings+= 1
		for key in main_hub:
			"Gets the data according to the current number of readings"
			data = generate_error_free_data(main_hub[key], current_number_of_readings)
			plot_station(main_hub[key], data, figures_in_graph_count, width, height, figure)
			figures_in_graph_count += 1 #creates a figure for every station
		
		plt.draw()
		plt.show()
		time.sleep(oscilation_time)
		if current_number_of_readings < number_of_readings:
			plt.clf()
		figures_in_graph_count = 1 #initializes the number of figures so that no extra figures are added

	return data

def main():
	#random generator, uses seeds for testing purposes if you want repeatability
	random_generator = random.Random(1) 
	#error parameters
	probability_of_erroneous_reading = 0.05
	erroneous_reading_standard_deviation = 20
	number_of_continous_erroneous_readings = 10

	#sensor parameters
	number_of_sensors_per_station = 1
	number_of_readings = 10
	actual_temperature = 20
	sensor_standard_deviation = 2
	station_standard_deviation = 2
	global_temperature = 20
	list_of_station_shifts = [10, -7, 2, -2]

	station_names = ["A", "B", "C", "D"] #name of the stations
	main_hub = {} #creates a dictionary to keep stations

	#create an station
	station_a = st.Station(global_temperature + list_of_station_shifts[0], 
		station_standard_deviation, station_names[0], random_generator)

	#add multiple sensors to station
	station_a.add_sensor_to_station(1, sensor_standard_deviation)
	station_a.add_sensor_to_station(2, sensor_standard_deviation)
	#station_a.add_sensor_to_station(3, sensor_standard_deviation)
	#station_a.add_sensor_to_station(4, sensor_standard_deviation)
	#station_a.add_sensor_to_station(5, sensor_standard_deviation)

	#connect sensors so that they are able to send data through each other
	#station_a.connect_sensors("E", "D")
	#station_a.connect_sensors("E", "C")
	#station_a.connect_sensors("D", "B")
	#station_a.connect_sensors("D", "C")
	#station_a.connect_sensors("B", "A")
	#station_a.connect_sensors("C", "A")

	station_b = st.Station(global_temperature + list_of_station_shifts[1], 
		station_standard_deviation, station_names[1], random_generator)

	station_b.add_sensor_to_station(1, sensor_standard_deviation)
	station_b.add_sensor_to_station(2, sensor_standard_deviation)
	station_b.add_sensor_to_station(3, sensor_standard_deviation)
	station_b.add_sensor_to_station(4, sensor_standard_deviation)
	station_b.add_sensor_to_station(5, sensor_standard_deviation)
	station_b.add_sensor_to_station(6, sensor_standard_deviation)
	station_b.add_sensor_to_station(7, sensor_standard_deviation)
	"""
	station_b.connect_sensors("E", "D")
	station_b.connect_sensors("E", "C")
	station_b.connect_sensors("D", "B")
	station_b.connect_sensors("C", "B")
	station_b.connect_sensors("C", "A")
	station_b.connect_sensors("B", "A")
	"""
	station_c = st.Station(global_temperature + list_of_station_shifts[2], 
		station_standard_deviation, station_names[2], random_generator)

	station_c.add_sensor_to_station(1, sensor_standard_deviation)
	station_c.add_sensor_to_station(2, sensor_standard_deviation)
	station_c.add_sensor_to_station(3, sensor_standard_deviation)
	station_c.add_sensor_to_station(4, sensor_standard_deviation)
	station_c.add_sensor_to_station(5, sensor_standard_deviation)
	"""
	station_c.connect_sensors("E", "C")
	station_c.connect_sensors("D", "E")
	station_c.connect_sensors("D", "C")
	station_c.connect_sensors("C", "B")
	station_c.connect_sensors("C", "A")
	station_c.connect_sensors("B", "A")
	"""
	station_d = st.Station(global_temperature + list_of_station_shifts[3], 
		station_standard_deviation, station_names[3], random_generator)

	station_d.add_sensor_to_station(1, sensor_standard_deviation)
	station_d.add_sensor_to_station(2, sensor_standard_deviation)


	main_hub[station_names[0]] = station_a
	#main_hub[station_names[1]] = station_b
	#main_hub[station_names[2]] = station_c
	#main_hub[station_names[3]] = station_d

	#data from one station
	data = generate_error_free_data(main_hub[station_names[0]], number_of_readings)
	data_with_erroneous_readings = add_erroneous_readings_to_data(data, 
		probability_of_erroneous_reading, erroneous_reading_standard_deviation, random_generator)
	
	data_with_continous_erroneous_readings = add_erroneous_continuous_sequence_to_data(data, 
		probability_of_erroneous_reading, number_of_continous_erroneous_readings, random_generator)

	figure = plt.figure()
	width = 1
	height = 3

	plot_station(main_hub[station_names[0]], data, 1, width, height, "Data no errors", figure)
	plot_station(main_hub[station_names[0]], data_with_erroneous_readings, 2, width, height, 
		"Data with errors", figure)
	plot_station(main_hub[station_names[0]], data_with_continous_erroneous_readings, 3, 
		width, height, "Data with continous sequence of errors", figure)
	plt.show()
	dataset = ["Sensor id", "Time", "Reading"]



	data_label = [] #to hold the labels of each sensor
	oscilation_time = 2 #time in seconds

	#data = read_data_over_time(main_hub, number_of_readings, oscilation_time, width, height)
	#data.insert(0, dataset)
	#save_data_to_file(data, "data.csv")

main()