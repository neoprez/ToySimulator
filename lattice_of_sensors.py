import random
import matplotlib.pyplot as plt
import sensor
import csv
import neuralnet
import math
import conx
import sys
import os
import linked_list
import numpy as np
import file_tools as ft
import error_rare_event_generator as error_generator
import time_series_tools as tstools
import lattice

def add_continous_erroneous_reading_to_sensor(sensor, probability_of_erroneous_reading, 
	number_of_continous_erroneous_readings, random_generator):
	"""
	This function adds a sequence erroneous readings to a single sensor time series. 
	This function modifies the sensor's original time series.
	"""
	time_series = sensor.get_time_series()
	erroneous_reading = error_generator.add_erroneous_continuous_sequence_to_time_series(time_series, 
		probability_of_erroneous_reading, number_of_continous_erroneous_readings, warmup_time, random_generator)
	erroneous_reading = tstools.normalize_to_range(erroneous_reading, 1.0)
	sensor.set_time_series(erroneous_reading)
	return erroneous_reading

def add_erroneous_reading_to_sensor(sensor, probability_of_erroneous_reading, 
	erroneous_reading_standard_deviation, warmup_time, random_generator):
	"""
	This function adds erroneous readings to a single sensor time series. 
	This function modifies the sensor's original time series.
	"""
	time_series = sensor.get_time_series()
	erroneous_reading = error_generator.add_erroneous_reading_to_time_series(time_series, 
		probability_of_erroneous_reading, erroneous_reading_standard_deviation, warmup_time, random_generator)
	erroneous_reading = tstools.normalize_to_range(erroneous_reading, 1.0) #normalize to be between 0 and 1
	sensor.set_time_series(erroneous_reading)
	return erroneous_reading

def add_erroneous_drift_towards_a_value_to_sensor(sensor, probability_of_erroneous_reading, 
	number_of_erroneous_points, random_generator):
	"""
	This function adds erroneous drift to a single sensor time series. 
	This function modifies the sensor's original time series.
	"""
	time_series = sensor.get_time_series()
	erroneous_reading = error_generator.add_erroneous_drift_towards_a_value(time_series, 
		probability_of_erroneous_reading, number_of_erroneous_points, random_generator)
	erroneous_reading = tstools.normalize_to_range(erroneous_reading, 1.0) #normalize
	sensor.set_time_series(erroneous_reading)
	return erroneous_reading

def add_errors(lattice_of_sensors, random_generator):
	"This function adds an error to a sensor in the lattice of sensors"
	number_of_continous_erroneous_readings = 500
	probability_of_erroneous_reading = 0.001
	erroneous_reading_standard_deviation = 0.20
	number_of_erroneous_points = 500

	sensor_to_insert_errors = lattice_of_sensors.get_sensor(0,0);
	add_erroneous_reading_to_sensor(sensor_to_insert_errors,
	 probability_of_erroneous_reading, 
	erroneous_reading_standard_deviation, warmup_time, random_generator)

def add_rare_event(file_name, lattice_of_sensors, random_generator):
	"This function adds a rare event to a time series in the sensors"
	max_dist = 2
	min_hearable_volume = 0.1 #volume at which the farthest sensor will listen to the rare son
	rare_event_song = ft.get_data_from_file(file_name)
	loudness = 0.9 #volume of reading at which the principal sensor is going to listen the rare song
	start_index, end_index = error_generator.generate_rare_event_for_random_period_of_time(lattice_of_sensors, max_dist, min_hearable_volume, 
	loudness, rare_event_song[0], random_generator)

	return lattice_of_sensors.gather_time_series_from_all_sensors(), start_index, end_index


def differentiate_errors_from_rare_event():
	warmup_time = 1500 #warmup for 1500 data points
	error_threshold = 0.02

	"Neural network"
	neural_net = create_neural_network(dimension_of_lattice**2)
	rmse_data, number_of_errors_detected, \
	list_of_errors_detected_in_each_time_point = run_neural_net_in_all_data(neural_net, lattice_of_sensors, number_of_time_points, warmup_time, error_threshold)

	print "list of errors detected",len(list_of_errors_detected_in_each_time_point)

	number_of_sensors_that_deviate_and_is_rare_event = number_of_sensors_deviating_vs_rare_event(start_index, end_index, list_of_errors_detected_in_each_time_point)
	save_data_to_file(number_of_sensors_that_deviate_and_is_rare_event, "number_of_sensors_that_deviate_and_is_rare_event.csv")

def main():
	dimension_of_lattice = 4 #dimension of the lattice of sensors. A square grid
	random_generator = random.Random()
	#assigns the values to the sensor based on the location of the sensors in the lattice
	list_of_time_series = ft.get_data_from_file("the_series.csv")
	lattice_of_sensors = lattice.Lattice(dimension_of_lattice)
	lattice_of_sensors.set_time_series_according_to_sensor_weight(list_of_time_series)

	time_series = lattice_of_sensors.gather_time_series_from_all_sensors()
	ft.save_data_to_file(time_series, "sensors_before_rare_event.csv")

	rare_time_series, start_index, end_index = add_rare_event("rare_song.csv", lattice_of_sensors, random_generator)
	ft.save_data_to_file(rare_time_series, "sensors_after_rare_event.csv")
main()