import random
import sensor
import csv
import file_tools as ft
import error_rare_event_generator as error_generator
import time_series_tools as tstools
import lattice
import stat_tools as stats
import sys

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
	erroneous_reading, number_of_errors_inserted = error_generator.add_erroneous_reading_to_time_series(time_series, 
		probability_of_erroneous_reading, erroneous_reading_standard_deviation, warmup_time, random_generator)
	erroneous_reading = tstools.normalize_to_range(erroneous_reading, 1.0) #normalize to be between 0 and 1
	sensor.set_time_series(erroneous_reading)
	return erroneous_reading, number_of_errors_inserted

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

def add_errors(lattice_of_sensors, random_generator, warmup_time, probability_of_erroneous_reading):
	"This function adds an error to a sensor in the lattice of sensors"
	number_of_continous_erroneous_readings = 500
	#probability_of_erroneous_reading = 0.001
	erroneous_reading_standard_deviation = 0.20
	number_of_erroneous_points = 500

	sensor_to_insert_errors = lattice_of_sensors.get_sensor(0,0);
	erroneous_readings, number_of_errors_inserted = add_erroneous_reading_to_sensor(sensor_to_insert_errors,
	 probability_of_erroneous_reading, 
	erroneous_reading_standard_deviation, warmup_time, random_generator)

	return lattice_of_sensors.gather_time_series_from_all_sensors(), number_of_errors_inserted

def add_rare_event(file_name, lattice_of_sensors, random_generator, max_dist):
	"This function adds a rare event to a time series in the sensors"
	#max_dist = 2
	min_hearable_volume = 0.1 #volume at which the farthest sensor will listen to the rare son
	rare_event_song = ft.get_data_from_file(file_name)
	loudness = 0.9 #volume of reading at which the principal sensor is going to listen the rare song
	start_index, end_index = error_generator.generate_rare_event_for_random_period_of_time(lattice_of_sensors, max_dist, min_hearable_volume, 
	loudness, rare_event_song[0], random_generator)

	return lattice_of_sensors.gather_time_series_from_all_sensors(), start_index, end_index

def differentiate_errors_from_rare_event(lattice_of_sensors, number_of_time_points, warmup_time, error_threshold):
	"""
	This functions runs the neural net in the lattice of sensors, returns the results. 
	RMSE, number_of_errors_detected and list_of_errors_detected_in_each_time_point
	"""

	"Neural network"
	neural_net = stats.create_neural_network(lattice_of_sensors.number_of_sensors) #creates a neural network with number_of_sensors nodes

	return stats.run_neural_net_in_all_data(neural_net, lattice_of_sensors, number_of_time_points, 
	warmup_time, error_threshold)


def save_data_to_file(list_of_data, list_of_file_names):
	"This function save all the data from the list into csv files"
	for data, name in zip(list_of_data, list_of_file_names):
		ft.save_data_to_file(data, name)


def main():
	
	dimension_of_lattice = 10 #dimension of the lattice of sensors. A square grid
	random_generator = random.Random()
	number_of_time_points = 0
	warmup_time = 1500 #warmup for 1500 data points
	error_threshold = 0.02
	run_id = ""

	if len(sys.argv) >= 2:
		run_id = str(sys.argv[1])

	#assigns the values to the sensor based on the location of the sensors in the lattice
	list_of_time_series = ft.get_data_from_file("the_series_normalized_1.csv")
	lattice_of_sensors = lattice.Lattice(dimension_of_lattice)
	lattice_of_sensors.set_time_series_according_to_sensor_weight(list_of_time_series)
	number_of_time_points = len(list_of_time_series[0])

	#probability_of_erroneous_reading = ((float(run_id) - 1)/2.0) * 0.1 #uses the run id to set the probability for errors
	#print probability_of_erroneous_reading
	max_dist = int(run_id)/10
	print "max dist", max_dist
	#time_series_before_rare_event = lattice_of_sensors.gather_time_series_from_all_sensors()
	#time_series_with_errors, number_of_errors_inserted = add_errors(lattice_of_sensors, random_generator, warmup_time, probability_of_erroneous_reading)
	time_series_after_rare_event, start_index, end_index = add_rare_event("rare_song_normalized_1.csv", lattice_of_sensors, random_generator, max_dist)

	rmse_data, number_of_errors_detected, list_of_errors_detected_in_each_time_point = differentiate_errors_from_rare_event(lattice_of_sensors, 
		number_of_time_points, warmup_time, error_threshold)
	#number_of_sensors_that_deviate_and_is_rare_event = stats.number_of_sensors_deviating_vs_rare_event(start_index, 
	#	end_index, list_of_errors_detected_in_each_time_point)

	save_data_to_file([list_of_errors_detected_in_each_time_point, [[start_index, end_index]]],
		["list_of_errors_detected_in_each_time_point_"+run_id+".csv", "rare_from_to_"+run_id+".csv"])
	"""save_data_to_file([rmse_data, [[number_of_errors_inserted, number_of_errors_detected]]],
		["rmse_data"+run_id+".csv", "number_of_errors_inserted_vs_errors_detected_"+run_id+".csv" ]
		)

	time_series_after_rare_event,
		 number_of_sensors_that_deviate_and_is_rare_event, time_series_with_errors
	rmse_data, [[number_of_errors_inserted, number_of_errors_detected]] ], 
		["rmse_data"+run_id+".csv", "number_of_errors_inserted_vs_errors_detected_"+run_id+".csv" ]
		, 
		"sensors_after_rare_event.csv", "number_of_sensors_that_deviate_and_is_rare_event.csv",
		"sensors_after_inserting_errors.csv""sensors_after_inserting_errors.csv""sensors_before_rare_event.csv"
	"""

main()