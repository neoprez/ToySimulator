"""
This file will only generate the time series to a file
"""
import random
import matplotlib.pyplot as plt
import sensor
import neuralnet
import math
import conx
import sys
import os
import linked_list
import numpy as np
import file_tools as ft
import time_series_tools as tstools

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
		"Returns the root mean square for a particular value"
		return math.sqrt(pow(val - expected_val, 2))

	def is_error(rmse):
		if rmse > error_threshold:
			return True
		
		return False

	def does_a_sensor_deviates_from_prediction(prediction, next_times_series):
		for i in range(len(next_times_series)):
			rmse = get_rmse_for_particular_value(prediction[i], next_times_series[i])
			if is_error(rmse):
				return True

		return False

	def does_deviates_from_prediction(prediction, observed_value):
		return is_error(get_rmse_for_particular_value(prediction, observed_value))

	def get_sensors_that_deviate_from_prediction(prediction, next_times_series):
		sensors_reporting_erroneous_data = []

		for i in range(len(next_times_series)):
			if does_deviates_from_prediction(prediction[i], next_times_series[i]):
				sensors_reporting_erroneous_data.append(i) if i not in sensors_reporting_erroneous_data else 0

		return sensors_reporting_erroneous_data

	def is_rare_event(next_times_series, error_tracker, sensors_that_deviate_from_prediction, time):
		"""
		Check if there is a correlation between the change in values among the sensors 
		that deviate from prediction at a time point.
		"""
		history = []
		count_of_sensors = 0
		max_index = error_tracker[0].get_node_count()

		for sensor_id in sensors_that_deviate_from_prediction:
			history = error_tracker[sensor_id]

			previous_flag = history.get_node_at(0).val
			idx = 1

			while idx < max_index:
				next_flag = history.get_node_at(idx).val
				idx += 1
				if previous_flag == 1 and next_flag == 1:
					count_of_sensors+= 1
					break
				else:
					break

		if count_of_sensors > len(sensors_that_deviate_from_prediction)/2:
			return True
		else:
			return False

		for idx in range(len(sensors_that_deviate_from_prediction) - 1):
			"look at the sensors that are the closest, to find their deviation"
			sensor_id_a = sensors_that_deviate_from_prediction[idx]
			sensor_id_b = sensors_that_deviate_from_prediction[idx + 1]
			reading_a = next_times_series[sensor_id_a]
			reading_b = next_times_series[sensor_id_b]

	def check_history_of_erroneous_sensors(error_tracker, sensors_reporting_erroneous_data):
		for sensor_index in sensors_reporting_erroneous_data:
			"Look at the flags of the previous readings"
			flags_list = error_tracker[sensor_index]
			length_of_error = 0
			cur_flag_index = 0
			node = flags_list.get_node_at(cur_flag_index)
			
			while node is not None:
				if node.val == 1: 
					length_of_error += 1
				else:
					break
				cur_flag_index += 1
				node = flags_list.get_node_at(cur_flag_index)

			if length_of_error > 1:
				print "Is rare event"
			else:
				print "Is error"

	def is_continous_value(sensor_id, time, error_tracker):
		history = error_tracker[sensor_id]
		value_to_stop_at = time #start at the latest time
		index = 0
		previous_flag = history.get_node_at(index).val
		index += 1
		max_index = history.get_node_count()
		nodes_since_last_error = 0

		while index < max_index:
			next_flag = history.get_node_at(index).val

			if previous_flag == 1 and next_flag == 1:
				return True

			if previous_flag == 1 and next_flag == 0:
				return False

			previous_flag = next_flag
			index += 1
			value_to_stop_at -= 1
		#print "after change"
		return False

	def is_drift_towards_a_value():
		pass

	def is_a_spike(sensor_id, time, error_tracker):
		history = error_tracker[sensor_id]
		time_to_stop_at = time
		index = 0
		previous_flag = history.get_node_at(index).val
		index += 1
		max_index = history.get_node_count()
		nodes_since_last_error = 0
		next_flag = 0

		while index < max_index:
			next_flag = history.get_node_at(index).val

			if previous_flag == 1 and next_flag == 0:
				break#return True

			if previous_flag == 1 and next_flag == 1:
				return False

			previous_flag = next_flag
			index += 1
			time_to_stop_at -= 1

		#for i in range(time, time_to_stop_at - 2, -1):
			#print i
		#print "after change"
		return True

	def flag_readings(sensors_that_deviate_from_prediction, error_tracker):
		for i in range(len(error_tracker)):
			if i in sensors_that_deviate_from_prediction:
				error_tracker[i].insert_first(1)
			else:
				error_tracker[i].insert_first(0)

	errors_over_time = []
	total_error = 0.0
	rmse_data = []
	sensors_reporting_erroneous_data = [] #list of sensors that are reporting wrong data
	list_of_predicted_values_to_change_for_errors = []
	error_tracker = []
	inputs = []
	number_of_sensors_in_lattice = len(lattice_of_sensors)**2

	for i in range(number_of_sensors_in_lattice):
		error_tracker.append(linked_list.LinkedList())

	time_since_previous_error = 0
	history_of_sensors_with_errors = []
	number_of_erroneous_readings = 0
	number_of_errors_detected = 0
	list_of_errors_detected_in_each_time_point = []
	list_non_erroneous_detections_at_each_time_point = []
	"To differentiate between a rare event and error I will use the number of sensors that change the readings"
	#number_of_sensors_that_deviate_from_prediction = 0
	#to keep track of the readings in each of the sensors.
	#if a sensor reports an error a flag is raised. If there is consistency in the flag among all the sensors
	#then we look at the previous readings of the sensors, if the previous reading reported a flag then we
	#consider it to be either an error or a rare event
	for time in range(1, number_of_time_points - 1):
		inputs.append(get_vector_of_time_series_from_all_sensors(time - 1)) #previous readings, keep track of them
		outputs = get_vector_of_time_series_from_all_sensors(time) #actual readings
		sensors_that_deviate_from_prediction = []
		number_of_sensors_that_deviate_from_prediction = 0

		if time > warmup_time: #run after the warm up period
			prediction = ask_neural_net(outputs) #checks if the prediction is ok
			next_times_series = get_vector_of_time_series_from_all_sensors(time + 1)
			rmse = get_rmse(prediction, next_times_series)

			#run only if a sensor deviates from prediction
			if does_a_sensor_deviates_from_prediction(prediction, next_times_series):
				#get how many sensors deviate from prediction
				sensors_that_deviate_from_prediction = get_sensors_that_deviate_from_prediction(prediction, next_times_series)
				number_of_sensors_that_deviate_from_prediction = len(sensors_that_deviate_from_prediction)

				list_of_errors_detected_in_each_time_point.append([number_of_sensors_that_deviate_from_prediction, time]) #1 for rare event
				#if more than one sensor is reporting erroneous data, assume is a rare event at first
				"Rare event prediction" 
				if number_of_sensors_that_deviate_from_prediction > 0:
					"Error prediction"
					"if the prediction deviates, train the network with the predicted value"
					#list_non_erroneous_detections_at_each_time_point.append([number_of_sensors_in_lattice - 1, 0])
					sensor_id = sensors_that_deviate_from_prediction[0] #get the id of the sensor that is reporting erroneous data
					history_of_sensors_with_errors.append(sensor_id)
					#print "Error at:", time
					number_of_errors_detected += 1
					if is_drift_towards_a_value():
						pass

					time_since_previous_error += 1
					#outputs[sensor_id] = prediction[sensor_id]
					#errors_over_time.append(rmse)
					number_of_erroneous_readings += 1
					total_error += rmse
			else:
				"Check if there was an error, to set the flag for history"
				#list_non_erroneous_detections_at_each_time_point.append([number_of_sensors_in_lattice, 0])
				#list_of_errors_detected_in_each_time_point.append([0, 1])
				list_of_errors_detected_in_each_time_point.append([number_of_sensors_that_deviate_from_prediction, time]) #1 for rare event
				if time_since_previous_error > 0:
					time_since_previous_error = (-1 * time_since_previous_error) #change sign to determine the amount of error
				else:
					time_since_previous_error = 0
			"Flag sensors reading, as  error or not error in history usin error_tracker"
			flag_readings(sensors_that_deviate_from_prediction, error_tracker)
			"Find the errors"
			if time_since_previous_error < 0:
				sensor_id = history_of_sensors_with_errors[-1]
				if is_rare_event(next_times_series, error_tracker, sensors_that_deviate_from_prediction, time):
					#print "Rare at time:", time
					pass
					#time_since_previous_error = 0

				if is_a_spike(sensor_id, time, error_tracker):
					"Get the value at 0 then at 1 then check the slope"
					#print "Spike error at time:", time
					pass
					#number_of_errors_detected += 1
				if is_continous_value(sensor_id, time, error_tracker):
					#print "Is continous at time:", time
					pass
					#number_of_errors_detected += 1
		#if there is something in the history use it as the input for trainig
		#trains with the predicted value if there is something in history
		neural_net.step(input = inputs[-1], output = outputs)

		if time <= warmup_time:
			#list_non_erroneous_detections_at_each_time_point.append([number_of_sensors_in_lattice, 0])
			prediction = ask_neural_net(outputs) #checks if the prediction is ok
			#list_of_errors_detected_in_each_time_point.append([0, 0, time]) #1 for rare event

		next_times_series = get_vector_of_time_series_from_all_sensors(time + 1)
		rmse = get_rmse(prediction, next_times_series)

		rmse_data.append([time, rmse])

	print "number of errors detected:", number_of_errors_detected
	print "Total Error:", str(total_error/number_of_time_points)
	return rmse_data, number_of_errors_detected, list_of_errors_detected_in_each_time_point

def number_of_sensors_deviating_vs_rare_event(initial_time_of_rare_event, end_time_of_rare_event, 
	number_of_sensors_that_deviate_from_prediction_over_time):

	number_of_sensors_that_deviate_and_is_rare_event = []

	for number_of_sensors_that_deviate_from_prediction, time in number_of_sensors_that_deviate_from_prediction_over_time:
		is_rare_event_time = time >= initial_time_of_rare_event and time <= end_time_of_rare_event
		number_of_sensors_that_deviate_and_is_rare_event.append([number_of_sensors_that_deviate_from_prediction, is_rare_event_time])

	return number_of_sensors_that_deviate_and_is_rare_event

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

def main():
	number_of_time_points = 20000 #number of time points to generate
	time_series_header = ["Time series A", "Time series B", "Time series C"]
	run_id = ""

	if len(sys.argv) >= 2:
		run_id = str(sys.argv[1])

	#we are using a lattice of sensors that reads data from different
	#songs. We combine the listening from 3 different readings.
	time_series = generate_predictable_parabola_time_series(number_of_time_points)
	time_series_b = generate_predictable_time_series(number_of_time_points) #series b
	time_series_c = generate_predictable_parabola_time_series(number_of_time_points, 100) #series c, right shift by 100
	rare_event_song = generate_predictable_sin_time_series(number_of_time_points)

	data_to_write = [time_series, time_series_b, time_series_c]

	ft.save_data_to_file(data_to_write, "the_series.csv")
	ft.save_data_to_file([rare_event_song], "rare_song.csv")

main()