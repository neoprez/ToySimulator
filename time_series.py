import random
import matplotlib.pyplot as plt
import sensor
import csv
import neuralnet
import math
import conx
import sys
import os

def generate_time_series(number_of_time_points):
	"This returns a list of randomly varying numbers"
	time_series = []
	number = 0

	for i in range(number_of_time_points):
		should_increase = random_generator.choice([True, False])

		if should_increase:
			number += 1
		else:
			number -= 1

		time_series.append(number)

	return time_series

def generate_predictable_time_series(number_of_time_points):
	"This retuns a predictable time series"
	return [x/100.0 for x in range(number_of_time_points)]

def generate_predictable_sin_time_series(number_of_time_points):
	return [math.sin(x/20.0) for x in range(number_of_time_points)]

def generate_predictable_parabola_time_series(number_of_time_points, shift=0):
	return [(x+shift)**2 for x in range(number_of_time_points)]

def normalize_to_range(time_series, desired_max=100):
	"""
	This function normalizes the data in time series to fall into the 
	desired range, between desired_min and desired_max.
	"""
	min_number = min(time_series)
	max_number = max(time_series) 

	if min_number == max_number:
		return [0] * len(time_series)
	else:
		min_coef = - min_number
		max_coef = desired_max / (max_number + min_coef * 1.0)
		return [(curr_number + min_coef) * max_coef for curr_number in time_series]

def merge_series(list_of_time_series, list_of_weights):
	"""
	This function merges a list of series into one according to their weight.
	"""
	merged_series = [0] * len(list_of_time_series[0])

	for idx in range(len(list_of_time_series)):
		coefficient_of_multiplication = list_of_weights[idx]
		series = list_of_time_series[idx]
		for index in range(len(series)):
			merged_series[index] = merged_series[index] + \
			(series[index] * coefficient_of_multiplication)
	return merged_series

def create_lattice_of_sensors(dimension, list_of_time_series):
	"Creates a latex of dimensions: dimension x dimension. Ex 4 x 4"
	lattice_of_sensors = []

	for row in range(dimension):
		list_of_sensors = []
		for col in range(dimension):
			weigth_from_b = row / (dimension * 1.0) #in vertical increase b 
			weigth_from_a = col / (dimension * 1.0) #in horizontal increase a
			weight_from_c = 0
			total_weight = weigth_from_a + weigth_from_b
			
			if total_weight < 1:
				weight_from_c = 1 - total_weight

			list_of_weights = [weigth_from_a, weigth_from_b, weight_from_c]
			time_series_for_sensor = merge_series(list_of_time_series, list_of_weights)
			time_series_for_sensor = normalize_to_range(time_series_for_sensor, 1)
			list_of_sensors.append(sensor.Sensor(time_series_for_sensor))
		lattice_of_sensors.append(list_of_sensors)

	return lattice_of_sensors

def save_data_to_file(data, file_name, mode="wb"):
	with open(file_name, mode) as csv_file:
		csv_writer = csv.writer(csv_file)
		for time_series in data:
			csv_writer.writerow(time_series)

def get_data_from_file(file_name, mode="rb"):
	data = []
	with open(file_name, mode) as csv_file:
		csv_reader = csv.reader(csv_file)
		for row in csv_reader:
			data.append(row)
	return data

def add_erroneous_reading_to_time_series(time_series, probability_of_erroneous_reading, 
	erroneous_reading_standard_deviation, random_generator):
	def get_erroneous_value(value):
		return random_generator.normalvariate(value, erroneous_reading_standard_deviation)

	def get_value_with_probabilistics_erroneous_value(value):
		if random_generator.random() < probability_of_erroneous_reading:
			return get_erroneous_value(value)
		return value

	return [get_value_with_probabilistics_erroneous_value(value) for value in time_series]

def add_erroneous_continuous_sequence_to_time_series(time_series, probability_of_erroneous_reading, 
	number_of_continous_erroneous_readings, random_generator):
	"""
	This function produces a continous sequence of erroneous readings. 
	Ex: 34, 35,35,35, 32, 38 ...
	"""
	def does_continous_erroneous_value_starts():
		return random_generator.random() < probability_of_erroneous_reading

	def insert_continous_value(value, start_index, data):
		end_index = min(start_index+number_of_continous_erroneous_readings, len(data))
		for i in range(start_index, end_index):
			data[i] = value
	
	modified_time_series = time_series[:]

	for idx in range(len(modified_time_series)): 
		if does_continous_erroneous_value_starts():
			value = modified_time_series[idx]
			insert_continous_value(value, idx, modified_time_series)

	return modified_time_series

def add_erroneous_drift_towards_a_value(time_series, probability_of_erroneous_reading, 
	number_of_erroneous_points, random_generator):
	"""
	This function adds erroneous drifts towards the a value.
	The value we are using is 0.
	"""
	def does_drift_towards_value_starts():
		return random_generator.random() < probability_of_erroneous_reading

	def drift_towards_a_value(series, value_to_drift, start_index, initial_reducing_percentage):
		end_index = min(start_index+number_of_erroneous_points, len(series))
		reducing_percentage = initial_reducing_percentage

		for idx in range(start_index, end_index):
			amount_to_subtract = value_to_drift * reducing_percentage
			series[idx] = value_to_drift - amount_to_subtract
			value_to_drift = series[idx]
			reducing_percentage += initial_reducing_percentage


	initial_reducing_percentage = (100.0/number_of_erroneous_points) * 0.01
	modified_time_series = time_series[:]

	for idx in range(len(modified_time_series)):
		if does_drift_towards_value_starts():
			value_to_drift = modified_time_series[idx]
			drift_towards_a_value(modified_time_series, value_to_drift, 
				idx, initial_reducing_percentage)

	return modified_time_series

def add_continous_erroneous_reading_to_sensor(sensor, probability_of_erroneous_reading, 
	number_of_continous_erroneous_readings, random_generator):
	"""
	This function adds a sequence erroneous readings to a single sensor time series. 
	This function modifies the sensor's original time series.
	"""
	time_series = sensor.get_time_series()
	erroneous_reading = add_erroneous_continuous_sequence_to_time_series(time_series, 
		probability_of_erroneous_reading, number_of_continous_erroneous_readings, random_generator)
	erroneous_reading = normalize_to_range(erroneous_reading, 1)
	sensor.set_time_series(erroneous_reading)

def add_erroneous_reading_to_sensor(sensor, probability_of_erroneous_reading, 
	erroneous_reading_standard_deviation, random_generator):
	"""
	This function adds erroneous readings to a single sensor time series. 
	This function modifies the sensor's original time series.
	"""
	time_series = sensor.get_time_series()
	erroneous_reading = add_erroneous_reading_to_time_series(time_series, 
		probability_of_erroneous_reading, erroneous_reading_standard_deviation, random_generator)
	erroneous_reading = normalize_to_range(erroneous_reading, 1) #normalize to be between 0 and 1
	sensor.set_time_series(erroneous_reading)

def add_erroneous_drift_towards_a_value_to_sensor(sensor, probability_of_erroneous_reading, 
	number_of_erroneous_points, random_generator):
	"""
	This function adds erroneous drift to a single sensor time series. 
	This function modifies the sensor's original time series.
	"""
	time_series = sensor.get_time_series()
	erroneous_reading = add_erroneous_drift_towards_a_value(time_series, 
		probability_of_erroneous_reading, number_of_erroneous_points, random_generator)
	erroneous_reading = normalize_to_range(erroneous_reading, 1) #normalize
	sensor.set_time_series(erroneous_reading)

def gather_time_series_from_sensors(lattice_of_sensors):
	"""
	This function collects the time series from the sensors in the lattice.
	"""
	collection_of_time_series = []
	for group_of_sensors in lattice_of_sensors:
		for sensor in group_of_sensors:
			sensor_data = sensor.get_time_series()
			collection_of_time_series.append(sensor_data)
	return collection_of_time_series
	

def generate_rare_event_to_lattice(lattice_of_sensors, max_dist, min_hearable_volume, 
	loudness, rare_event_song, random_generator):
	"""
	This function generates a rare event that is added to the readings of the sensors 
	in the lattice. The volume is reduces as it goes away from the initial sensor. 
	loudness - (loudness-min_hearable_volume)/(max_dist) * i 
	"""
	def get_a_random_sensor_index():
		"This function returns a random index to pick a sensor from lattice"
		start_index = 0
		end_index = len(lattice_of_sensors) - 1

		return random_generator.randint(start_index, end_index), \
		random_generator.randint(start_index, end_index)

	def change_sensor_time_series_to_rare_series(sensor, loudness_of_the_area):
		sensor_time_series = sensor.get_time_series()
		new_series = merge_series([rare_event_song, sensor_time_series], 
		[loudness_of_the_area, 1])
		new_series = normalize_to_range(new_series, 1) #normalize to 1
		sensor.set_time_series(new_series)

	def add_loudness_to_sensors_at_a_distance(current_distance_from_beginning, 
		row_of_first_ocurrence, col_of_first_ocurrence):
		"""
		This function adds loudnes to sensors in an area with respect to the distance from 
		first occurrence
		"""
		start_row = max(0, row_of_first_ocurrence - current_distance_from_beginning)
		start_col = max(0, col_of_first_ocurrence - current_distance_from_beginning)
		end_row = min(row_of_first_ocurrence + current_distance_from_beginning + 1, 
			len(lattice_of_sensors))
		end_col = min(col_of_first_ocurrence + current_distance_from_beginning + 1, 
		 	len(lattice_of_sensors))

		loudness_of_the_area = loudness - ((loudness - min_hearable_volume)/max_dist) * \
		  current_distance_from_beginning

		for r in range(start_row, end_row):
			for c in range(start_col, end_col):
				row_distance = abs(r - row_of_first_ocurrence)
				col_distance = abs(c - col_of_first_ocurrence)
				distance = max(row_distance, col_distance)
		 		
		 		if distance == current_distance_from_beginning:
		 			sensor = lattice_of_sensors[r][c]
		 			change_sensor_time_series_to_rare_series(sensor, loudness_of_the_area)

	#pick a random sensor
	row_of_first_ocurrence, col_of_first_ocurrence = get_a_random_sensor_index()
	print row_of_first_ocurrence, col_of_first_ocurrence
	sensor = lattice_of_sensors[row_of_first_ocurrence][col_of_first_ocurrence]
	change_sensor_time_series_to_rare_series(sensor, loudness)

	for current_distance in range(1, max_dist + 1):
		add_loudness_to_sensors_at_a_distance(current_distance, row_of_first_ocurrence, 
			col_of_first_ocurrence)

def create_neural_network(vector_size):
	"Creates a neural network"
	expert = conx.Network()
	expert.addLayer("input", vector_size)
	expert.addLayer("hidden", vector_size)
	expert.addLayer("output", vector_size)
	expert.connect("input", "hidden")
	expert.connect("hidden", "output")
	expert.resetEpoch = 1  #HOW MANY TIMES IS BEING TRAINED
	expert.resetLimit = 1
	expert.momentum = 0
	expert.epsilon = 0.5

	return expert

def run_neural_net_in_all_data(neural_net, lattice_of_sensors, number_of_time_points, 
	warmup_time, error_threshold):
	"""
	This function runs the neural network in all sensors.
	The warm up time specifies the number of time points needed fo the neural network to adjust
	the weights between sensors.
	"""
	def get_vector_of_time_series_from_all_sensors(time_point):
		vector_of_readings = []

		for sensor_group in lattice_of_sensors:
			for sensor in sensor_group:
				vector_of_readings.append(sensor.get_reading_at_time(time_point))

		return vector_of_readings
	def ask_neural_net(inpt):
		"""
		Find out what the expert predicts for the given input.
		"""
		neural_net['input'].copyActivations(inpt)
		neural_net.propagate()
		return neural_net['output'].activation

	def train_neural_net_on_all(inputs, outputs):
		neural_net.setInputs(inputs)
		neural_net.setOutputs(outputs)
		neural_net.train()

	def get_rmse(outputs, next_times_series):
		"""Returns the root mean square error from the two time series"""
		difference = []

		for i in range(len(outputs)):
			result = pow(outputs[i] - next_times_series[i], 2)
			difference.append(result)

		sum_of_differences = sum(difference)
		
		return math.sqrt(sum_of_differences)

	def train_neural_net(inputs, outputs):
		"Trains the neural network over the warm up period"
		for i in range(1, warmup_time + 1):
			inputs.append(get_vector_of_time_series_from_all_sensors(i - 1))
			outputs.append(get_vector_of_time_series_from_all_sensors(i))
			neural_net.step(input = inputs[-1], output = outputs[-1])

	def get_rmse_for_particular_value(val, expected_val):
		"Returns the rms for a particular value"
		return math.sqrt(pow(val - expected_val, 2))

	inputs = []
	outputs = []
	errors_over_time = []
	total_error = 0.0
	rmse_data = []
	#train_neural_net(inputs, outputs) #train the neural network
	flagged_data = [] #to hold the input that has errors
	sensors_reporting_erroneous_data = [] #list of sensors that are reporting wrong data
	"To differentiate between a rare event and error I will use the number of sensors that change the readings"
	number_of_sensors_that_deviate_from_prediction = 0
	
	for idx in range(1, number_of_time_points - 1):
		inputs.append(get_vector_of_time_series_from_all_sensors(idx - 1))
		outputs.append(get_vector_of_time_series_from_all_sensors(idx))
		neural_net.step(input = inputs[-1], output = outputs[-1])

		#train_neural_net_on_all(inputs, outputs)
		prediction = ask_neural_net(outputs[-1]) #checks if the prediction is ok
		next_times_series = get_vector_of_time_series_from_all_sensors(idx + 1)
		rmse = get_rmse(prediction, next_times_series)
		"Rare event"
		"Error prediction"
		if idx > warmup_time and rmse > error_threshold:
			"Flag the input that is giving the wrong value"
			"loop through all the data values and check which one differs the most from the expected value"
			cur_output = prediction
			for i in range(len(next_times_series)):
				rmse = get_rmse_for_particular_value(cur_output[i], next_times_series[i])
				if rmse > error_threshold:
					if number_of_sensors_that_deviate_from_prediction < 2:
						print "Sensor with errors is:", i, "at time:", idx
						if i not in sensors_reporting_erroneous_data:
							sensors_reporting_erroneous_data.append(i)
							number_of_sensors_that_deviate_from_prediction += 1
					else:
						if i not in sensors_reporting_erroneous_data:
							sensors_reporting_erroneous_data.append(i)
							number_of_sensors_that_deviate_from_prediction += 1
						print "Erroneous event\n", "Sensors reporting erroneous data:", number_of_sensors_that_deviate_from_prediction

			flagged_data.append(["Change at time", idx])

		errors_over_time.append(rmse)
		total_error += rmse
		rmse_data.append([idx, rmse])

		#print "Root mean se:", rmse, "i:", idx
	print "Total Error:", str(total_error/number_of_time_points)
	#plt.plot(errors_over_time)
	return rmse_data,flagged_data
	#plt.show()

def calculate_average_rmse_for_every_data_point_in_all_files(number_of_time_points):
	"""
	Calcualte the average rmse from all the files that contains the keyword 'rmse' in the current directory.
	returns a list containing the averaged value of all data points. 
	"""
	def add_data_to_averaged_rmse(rmse_series):
		for idx in range(1, len(rmse_series)): #1 to skip the column headers
			averaged_rmse_data[idx] += float(rmse_series[idx][1])
	#calculate average of rmse
	#-1 because we dont count the first and last time point
	averaged_rmse_data = [0] * (number_of_time_points - 1) 
	file_count = 0 #the divisor to for which we would divided every number in the calculated average

	#get a list of all files in directory
	for fl in os.listdir("."):
		if "rmse" in fl and fl.endswith(".csv"):
			rmse_series = get_data_from_file(str(fl)) #the data in a file
			add_data_to_averaged_rmse(rmse_series)
			file_count += 1
	#divide everything by the number of files in data points
	return [x/file_count for x in averaged_rmse_data if file_count > 0]

def get_data_with_col_headers_from_lattice_of_sensors(lattice_of_sensors, dimension_of_lattice, col_headers):
	"""
	Returns a list with the data from time series in all sensors in the lattice with column headers.
	"""
	def add_readings_from_time_series_to_data(data, sensor_time_series):
		for time in range(len(sensor_time_series)):
			data.append([sensor_number, (time+1), sensor_time_series[time]])

	data = []
	data.append(col_headers) #add the columns headers

	sensor_number = 1 #actual sensor from where the reading is taken
	for row in range(dimension_of_lattice):
		for col in range(dimension_of_lattice):
			sensor_time_series = lattice_of_sensors[row][col].get_time_series()
			add_readings_from_time_series_to_data(data, sensor_time_series)
			sensor_number += 1

	return data


def main():
	random_generator = random.Random()
	number_of_continous_erroneous_readings = 500
	probability_of_erroneous_reading = 0.001
	erroneous_reading_standard_deviation = 20
	number_of_erroneous_points = 100
	number_of_time_points = 30000
	input_vector_size = 1
	dimension_of_lattice = 4 #dimension of the lattice of sensors. A square grid
	warmup_time = 150 #warmup for 150 data points
	error_threshold = 0.02
	time_series_header = ["SENSOR NUMBER", "TIME", "READING"]
	rmse_header = ["TIME", "RMSE"]
	run_id = ""

	if len(sys.argv) >= 2:
		run_id = str(sys.argv[1])

	#we are using a lattice of sensors that reads data from different
	#songs. We combine the listening from 3 different readings.
	#time_series = generate_time_series(number_of_time_points) #series a
	time_series = generate_predictable_parabola_time_series(number_of_time_points)
	#time_series = generate_predictable_sin_time_series(number_of_time_points)
	#time_series = generate_predictable_parabola_time_series(number_of_time_points)
	#time_series_b = generate_time_series(number_of_time_points) #series b
	time_series_b = generate_predictable_time_series(number_of_time_points) #series b
	#time_series_b = generate_predictable_parabola_time_series(number_of_time_points)
	#time_series_b = generate_predictable_time_series(number_of_time_points) #series b
	#time_series_c = generate_time_series(number_of_time_points) #series c
	#time_series_c = generate_predictable_time_series(number_of_time_points) #series c
	#time_series_c = generate_predictable_sin_time_series(number_of_time_points) #series c
	time_series_c = generate_predictable_parabola_time_series(number_of_time_points, 100) #series c, right shift by 100
	#normalize the time series so that they fall in the same range. Our case 0 to 100
	normalized_time_series = normalize_to_range(time_series, 1.0)
	normalized_time_series_b = normalize_to_range(time_series_b, 1.0)
	normalized_time_series_c = normalize_to_range(time_series_c, 1.0)

	#assigns the values to the sensor based on the location of the sensors in the lattice
	list_of_time_series = [normalized_time_series, normalized_time_series_b, normalized_time_series_c]
	lattice_of_sensors = create_lattice_of_sensors(dimension_of_lattice, list_of_time_series)
	"Add errors"
	"Sensor (1,0), with errors"
	add_erroneous_drift_towards_a_value_to_sensor(lattice_of_sensors[1][0], probability_of_erroneous_reading, 
	number_of_erroneous_points, random_generator)
	"Sensor (0,0), with errors"
	add_erroneous_drift_towards_a_value_to_sensor(lattice_of_sensors[0][0], probability_of_erroneous_reading, 
	number_of_erroneous_points, random_generator)
	"Sensor (2,2) with errors"
	add_continous_erroneous_reading_to_sensor(lattice_of_sensors[2][2], probability_of_erroneous_reading, 
	number_of_continous_erroneous_readings, random_generator)
	
	"RARE EVENT at (3,3)"""
	max_dist = 2
	min_hearable_volume = 0.01 #volume at which the farthest sensor will listen to the rare son
	rare_event_song = generate_predictable_sin_time_series(number_of_time_points)
	loudness = 0.2 #volume of reading at which the principal sensor is going to listen the rare song
	#generate_rare_event_to_lattice(lattice_of_sensors, max_dist, min_hearable_volume, 
	#loudness, rare_event_song, random_generator) #picks a random sensor
	#add_erroneous_reading_to_sensor(lattice_of_sensors[3][3], probability_of_erroneous_reading, 
	#erroneous_reading_standard_deviation, random_generator)
	"Neural network"
	neural_net = create_neural_network(dimension_of_lattice**2)
	rmse_data, flagged_data = run_neural_net_in_all_data(neural_net, lattice_of_sensors, number_of_time_points, warmup_time, error_threshold)

	print "Number of errors:",len(flagged_data)
	rmse_data.insert(0, rmse_header)
	save_data_to_file(rmse_data, "rmse" + run_id + ".csv")
	data = get_data_with_col_headers_from_lattice_of_sensors(lattice_of_sensors, dimension_of_lattice, time_series_header)
	save_data_to_file(data, "time_series" + run_id + ".csv" )

	averaged_rmse_data = calculate_average_rmse_for_every_data_point_in_all_files(number_of_time_points)

	plt.plot(averaged_rmse_data)
	plt.show()

	the_data_for_file = []
	the_data_for_file.append(rmse_header)
	for i in range(1, len(averaged_rmse_data)):
		the_data_for_file.append([i, averaged_rmse_data[i]])
	save_data_to_file(the_data_for_file, "averaged_erm.csv")


	
	figure = plt.figure()
	normal_data = gather_time_series_from_sensors(lattice_of_sensors)
	axes_n = figure.add_subplot(1, 1, 1)
	transposed_data = map(list, zip(*normal_data))
	#print transposed_data
	axes_n.plot(transposed_data)
	#axes_n.legend(range(len(transposed_data)))
	plt.show()
	
main()