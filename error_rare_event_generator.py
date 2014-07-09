"This file is to insert error or rare events to csv files "
import random
import sensor
import csv
import math
import numpy as np
import file_tools as ft
import time_series_tools as tstools

def add_erroneous_reading_to_time_series(time_series, probability_of_erroneous_reading, 
	erroneous_reading_standard_deviation, warmup_time, random_generator):
	def get_erroneous_value(value):
		return random_generator.normalvariate(value, erroneous_reading_standard_deviation)

	def get_value_with_probabilistics_erroneous_value(value, idx):
		if random_generator.random() < probability_of_erroneous_reading and idx > warmup_time:
			return get_erroneous_value(value), 1
		return value, 0
	
	new_series = []
	count_of_errors = 0

	for i in range(len(time_series)):
		value = time_series[i]
		value, count = get_value_with_probabilistics_erroneous_value(value, i)
		count_of_errors += count
		new_series.append(value)

	return new_series, count_of_errors

def add_erroneous_continuous_sequence_to_time_series(time_series, probability_of_erroneous_reading, 
	number_of_continous_erroneous_readings, warmup_time, random_generator):
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
		return 1 #amount of errors inserted

	modified_time_series = time_series[:]
	number_of_errors_inserted = 0

	for idx in range(len(modified_time_series)): 
		if does_continous_erroneous_value_starts() and idx > warmup_time:
			value = modified_time_series[idx]
			number_of_errors_inserted += insert_continous_value(value, idx, modified_time_series)

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
		new_series = normalize_to_range(new_series, 1.0) #normalize to 1
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
	print row_of_first_ocurrence, col_of_first_ocurrence #print sensor where the rare event starts
	sensor = lattice_of_sensors[row_of_first_ocurrence][col_of_first_ocurrence]
	change_sensor_time_series_to_rare_series(sensor, loudness)

	for current_distance in range(1, max_dist + 1):
		add_loudness_to_sensors_at_a_distance(current_distance, row_of_first_ocurrence, 
			col_of_first_ocurrence)

def generate_rare_event_for_random_period_of_time(lattice_of_sensors, max_dist, min_hearable_volume, 
	loudness, rare_event_song, random_generator):
	"This function adds a rare event to the lattice of sensors, for a random period of time"
	def get_a_random_sensor_index():
		"This function returns a random index to pick a sensor from lattice"
		start_index = 0
		end_index = lattice_of_sensors.dimension_of_lattice - 1

		return random_generator.randint(start_index, end_index), \
		random_generator.randint(start_index, end_index)

	def get_random_period_of_time(max_time):
		"""
		Gets the start and end index that will be used to add the rare song to lattice
		max_time: the maximum amount of time that event can occur
		returns the start index and end index
		"""
		a = random_generator.randint(0, max_time) #from 0 to maximum time
		b = random_generator.randint(a, max_time) #from time a to maximum time
		print "Rare from:", a, "to", b
		print "Number of rare time points:", b-a
		return a, b

	def crop_time_series(series, start_index, end_index):
		cropped_series = []

		for i in range(start_index, end_index + 1):
			cropped_series.append(series[i])

		return cropped_series

	def change_sensor_time_series_to_rare_series(sensor, loudness_of_the_area, start_index, end_index):
		sensor_time_series = sensor.get_time_series()

		cropped_sensor_time_series = crop_time_series(sensor_time_series, start_index, end_index)
		cropped_rare_event_song = crop_time_series(rare_event_song, start_index, end_index)

		merged_series = tstools.merge_series([cropped_rare_event_song, cropped_sensor_time_series], 
		[loudness_of_the_area, 1])

		new_series = sensor_time_series[:]
		#to append previous valus to the new time series
		for i in range(len(merged_series)):
			new_series[start_index + i] = merged_series[i]

		new_series = tstools.normalize_to_range(new_series, 1.0) #normalize to 1
		sensor.set_time_series(new_series)

	def add_loudness_to_sensors_at_a_distance(current_distance_from_beginning, 
		row_of_first_ocurrence, col_of_first_ocurrence, start_index, end_index):
		"""
		This function adds loudnes to sensors in an area with respect to the distance from 
		first occurrence
		"""
		start_row = max(0, row_of_first_ocurrence - current_distance_from_beginning)
		start_col = max(0, col_of_first_ocurrence - current_distance_from_beginning)
		end_row = min(row_of_first_ocurrence + current_distance_from_beginning + 1, 
			lattice_of_sensors.dimension_of_lattice - 1)
		end_col = min(col_of_first_ocurrence + current_distance_from_beginning + 1, 
		 	lattice_of_sensors.dimension_of_lattice - 1)

		loudness_of_the_area = loudness - ((loudness - min_hearable_volume)/max_dist) * \
		  current_distance_from_beginning

		for r in range(start_row, end_row):
			for c in range(start_col, end_col):
				row_distance = abs(r - row_of_first_ocurrence)
				col_distance = abs(c - col_of_first_ocurrence)
				distance = max(row_distance, col_distance)
		 		
		 		if distance == current_distance_from_beginning:
		 			sensor = lattice_of_sensors.get_sensor(r, c)
		 			change_sensor_time_series_to_rare_series(sensor, loudness_of_the_area, start_index, end_index)

	#pick a random sensor
	row_of_first_ocurrence, col_of_first_ocurrence = get_a_random_sensor_index()
	#pick a random period of time
	start_index, end_index = get_random_period_of_time(len(rare_event_song))
	print "Sensor of initial occurrence:", row_of_first_ocurrence, col_of_first_ocurrence #print sensor where the rare event starts
	sensor = lattice_of_sensors.get_sensor(row_of_first_ocurrence,col_of_first_ocurrence)
	change_sensor_time_series_to_rare_series(sensor, loudness, start_index, end_index)

	for current_distance in range(1, max_dist + 1):
		add_loudness_to_sensors_at_a_distance(current_distance, row_of_first_ocurrence, 
			col_of_first_ocurrence, start_index, end_index)

	return start_index, end_index
