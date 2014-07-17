import random
import sensor
import csv
import file_tools as ft
import error_rare_event_generator as error_generator
import time_series_tools as tstools
import lattice
import stat_tools as stats
import sys

def add_continous_erroneous_reading_to_sensor(sensor, 
	probability_of_erroneous_reading, 
	number_of_continous_erroneous_readings, warmup_time, 
	random_generator):
	"""
	This function adds a sequence erroneous readings to a single sensor 
	time series. This function modifies the sensor's original 
	time series.
	"""
	time_series = sensor.get_time_series()
	
	erroneous_reading = \
	error_generator.add_erroneous_continuous_sequence_to_time_series(
		time_series, probability_of_erroneous_reading, 
		number_of_continous_erroneous_readings, warmup_time, 
		random_generator)

	erroneous_reading = tstools.normalize_to_range(erroneous_reading, 1.0)
	sensor.set_time_series(erroneous_reading)
	return erroneous_reading

def add_erroneous_reading_to_sensor(sensor, 
	probability_of_erroneous_reading, 
	erroneous_reading_standard_deviation, warmup_time, random_generator):
	"""
	This function adds erroneous readings to a single sensor time series. 
	This function modifies the sensor's original time series.
	"""
	time_series = sensor.get_time_series()
	erroneous_reading, number_of_errors_inserted, \
	list_of_errors_inserted = \
	error_generator.add_erroneous_reading_to_time_series(time_series, 
		probability_of_erroneous_reading, 
		erroneous_reading_standard_deviation, warmup_time, 
		random_generator)
	
	#normalize to be between 0 and 1
	erroneous_reading = tstools.normalize_to_range(erroneous_reading, 1.0) 
	sensor.set_time_series(erroneous_reading)
	return erroneous_reading, number_of_errors_inserted, list_of_errors_inserted

def add_erroneous_drift_towards_a_value_to_sensor(sensor, 
	probability_of_erroneous_reading, number_of_erroneous_points, 
	random_generator):
	"""
	This function adds erroneous drift to a single sensor time series. 
	This function modifies the sensor's original time series.
	"""
	time_series = sensor.get_time_series()

	erroneous_reading = \
	error_generator.add_erroneous_drift_towards_a_value(time_series, 
		probability_of_erroneous_reading, number_of_erroneous_points, 
		random_generator)

	#normalize
	erroneous_reading = tstools.normalize_to_range(erroneous_reading, 1.0) 
	sensor.set_time_series(erroneous_reading)
	return erroneous_reading

def add_errors(sensor_to_insert_errors, lattice_of_sensors, choice, probability_of_erroneous_reading, 
	erroneous_reading_standard_deviation, number_of_continous_erroneous_readings, 
	warmup_time, random_generator, run_id = ""):

	if choice == 1:
		"Insert spike error"
		time_series_with_errors, number_of_errors_inserted, list_of_times_when_errors_were_inserted = insert_type_of_error_to_sensor(
		sensor_to_insert_errors,1, 
		probability_of_erroneous_reading,erroneous_reading_standard_deviation, 
		number_of_continous_erroneous_readings, warmup_time, random_generator)

		"save data to file"
		all_series_with_errors = lattice_of_sensors.gather_time_series_from_all_sensors()
		save_data_to_file([all_series_with_errors], ["time_series_with_spike_errors_"+str(run_id)+".csv"])

	elif choice == 2:
		"Insert Continous error"
		time_series_with_errors = insert_type_of_error_to_sensor(sensor_to_insert_errors,
		2, probability_of_erroneous_reading,
		erroneous_reading_standard_deviation, number_of_continous_erroneous_readings,
		warmup_time, random_generator)

		"save data to file"
		all_series_with_errors = lattice_of_sensors.gather_time_series_from_all_sensors()
		save_data_to_file([all_series_with_errors], ["time_series_with_continous_errors_"+str(run_id)+".csv"])

	else:
		number_of_sensors_to_insert_error =  int(prompt_for_input("How many sensors do you want to insert error?"))
		"Insert Multiple type of errors"
		for _ in range(number_of_sensors_to_insert_error):
			error_type = int(prompt_for_input("Enter error type:"))
			r, c = ask_sensor_to_insert_error()
			sensor_to_insert_errors = lattice_of_sensors.get_sensor(int(r), int(c))

			insert_type_of_error_to_sensor(sensor_to_insert_errors, error_type, probability_of_erroneous_reading,
			erroneous_reading_standard_deviation, number_of_continous_erroneous_readings,
			warmup_time, random_generator)

		"save data to file"
		all_series_with_errors = lattice_of_sensors.gather_time_series_from_all_sensors()
		save_data_to_file([all_series_with_errors], ["time_series_with_multiple_errors_"+str(run_id)+".csv"])

def add_rare_event(lattice_of_sensors, rare_event_song, random_generator, 
	max_dist, loudness, min_hearable_volume, run_id =""):
	"This function adds a rare event to a time series in the sensors"
	start_index, end_index = \
	error_generator.generate_rare_event_for_random_period_of_time(
		lattice_of_sensors, max_dist, min_hearable_volume, 
	loudness, rare_event_song, random_generator)

	sensors_after_rare_event = lattice_of_sensors.gather_time_series_from_all_sensors()
	save_data_to_file([sensors_after_rare_event], ["sensors_after_rare_event_"+str(run_id)+".csv"])

	return sensors_after_rare_event, start_index, end_index

def differentiate_errors_from_rare_event(lattice_of_sensors, 
	number_of_time_points, warmup_time, error_threshold):
	"""
	This functions runs the neural net in the lattice of sensors, 
	returns the results. RMSE, number_of_errors_detected and 
	list_of_errors_detected_in_each_time_point
	"""

	"Neural network"
	#creates a neural network with number_of_sensors nodes
	neural_net = stats.create_neural_network(
		lattice_of_sensors.number_of_sensors) 

	return stats.run_neural_net_in_all_data(neural_net, 
		lattice_of_sensors, number_of_time_points, warmup_time, 
		error_threshold)


def save_data_to_file(list_of_data, list_of_file_names):
	"This function save all the data from the list into csv files"
	for data, name in zip(list_of_data, list_of_file_names):
		ft.save_data_to_file(data, name)

def check_for_true_positives(list_of_times_when_errors_were_inserted, 
	list_of_errors_detected_in_each_time_point):
	"""
	This function checks if the errors detected are true positives. 
	Returns a list containing the time at which any point was detected 
	and a number, 1 for true positive, 0 for false positives.
	"""
	list_of_true_positives = []
	list_of_false_positives = []

	for sensors, time in list_of_errors_detected_in_each_time_point:
		if sensors > 0:
			"check if it is true positive or false positive"
			if time in list_of_times_when_errors_were_inserted:
				list_of_true_positives.append([time, 1])
			else:
				list_of_false_positives.append([time, 1])
		else:
			if time in list_of_times_when_errors_were_inserted:
				list_of_false_positives.append([time, 1])
			else:
				list_of_true_positives.append([time, 1])

	return list_of_true_positives, list_of_false_positives

def prompt_for_input(message):
	print message,
	return raw_input()

def ask_sensor_to_insert_error():
	"This function ask the user for row and col of a sensor"

	input_from_user = prompt_for_input("Enter sensor (row and column) " \
		 + "to insert error separated by comma:").split(",")
	r = input_from_user[0] #row
	c = input_from_user[1] #col

	return r,c

def insert_type_of_error_to_sensor(sensor_to_insert_errors, error_type, 
	probability_of_erroneous_reading, erroneous_reading_standard_deviation, 
	number_of_continous_erroneous_readings, warmup_time, random_generator):

	"""
	This function inserts the error_type to the sensor. 
	Returns time_series_with_errors, 
	number_of_errors_inserted, list_of_times_when_errors_were_inserted
	if error type is spike(1) else if error_type is Continous(2)
	returns time_series_with_errors
	"""
	if error_type == 1:
		return add_erroneous_reading_to_sensor(sensor_to_insert_errors, 
		probability_of_erroneous_reading, 
		erroneous_reading_standard_deviation, warmup_time, 
		random_generator)
	else:
		return add_continous_erroneous_reading_to_sensor(
			sensor_to_insert_errors, probability_of_erroneous_reading, 
			number_of_continous_erroneous_readings, warmup_time, 
			random_generator)

def initialize_lattice(list_of_time_series):
	dimension_of_lattice = int(prompt_for_input("Enter dimension of lattice:"))
	lattice_of_sensors = lattice.Lattice(dimension_of_lattice) #create the lattice of sensors
	lattice_of_sensors.set_time_series_according_to_sensor_weight(list_of_time_series) #assigns deterministic functions to sensors
	return lattice_of_sensors

def get_list_of_time_series():
	name_of_file_of_time_series = prompt_for_input("Enter name of file of time series:")
	return ft.get_data_from_file(name_of_file_of_time_series)

def show_error_menu(lattice_of_sensors, random_generator, probability_of_erroneous_reading = 0.001, 
			erroneous_reading_standard_deviation = 0.20, number_of_continous_erroneous_readings = 500,
			warmup_time = 1500):
	"This function shows an error menu"

	print "You are adding errors!"
	print "What type of errors do you want to insert:"
	choice = int(prompt_for_input("1 - Spike in reading \n2 - Continous reading \n3 - Multiple type \n?: "))
	should_use_default_parameters = True if prompt_for_input("Do you want to use default parameters? yes/no:") == "yes" else False

	"To change default parameters"
	if not should_use_default_parameters:
		probability_of_erroneous_reading = float(prompt_for_input("Enter probability of erroneous reading:"))
		number_of_continous_erroneous_readings = int(prompt_for_input("Enter number of continous erroneous points"))
		warmup_time = int(prompt_for_input("Enter warm up time:"))
		erroneous_reading_standard_deviation = float(prompt_for_input("Enter erroneous reading standard deviation:"))

	"Add errors"
	r, c = ask_sensor_to_insert_error()
	sensor_to_insert_errors = lattice_of_sensors.get_sensor(int(r), int(c))

	add_errors(sensor_to_insert_errors, lattice_of_sensors, choice, probability_of_erroneous_reading, 
		erroneous_reading_standard_deviation, number_of_continous_erroneous_readings, warmup_time, random_generator)

def show_rare_event_menu(lattice_of_sensors, random_generator, min_hearable_volume = 0.1,
	error_threshold = 0.02, loudness = 0.3, max_dist = 1):
	"This functions shows a rare event menu. file name usually: rare_song_normalized.csv"
	print "You are adding a rare event!!"
	file_name = prompt_for_input("Enter rare song file name:")
	rare_event_song = ft.get_data_from_file(file_name)

	should_use_default_parameters = True if prompt_for_input("Do you want to use default parameters? yes/no:") == "yes" else False

	if not should_use_default_parameters:
		error_threshold = float(prompt_for_input("Enter error threshold:"))
		loudness = float(prompt_for_input("Enter loudness:"))
		min_hearable_volume = float(prompt_for_input("Enter min_hearable_volume:"))
		max_dist = int(prompt_for_input("Enter max distance:"))

	add_rare_event(lattice_of_sensors, rare_event_song[0], random_generator, max_dist, 
		loudness, min_hearable_volume)

def create_error_free_data(lattice_of_sensors, run_id =""):
	all_error_free_series = lattice_of_sensors.gather_time_series_from_all_sensors()
	save_data_to_file([all_error_free_series], ["all_error_free_series"+str(run_id)+".csv"])
	print "You have created an error-free time series!"

def show_main_menu(random_generator):

	"File of time series is usually a normalized time series. the_series_normalized.csv"
	list_of_time_series = get_list_of_time_series()

	"initialize lattice of sensors"
	lattice_of_sensors = initialize_lattice(list_of_time_series)

	"Should add errors?"
	do_add_errors = True if prompt_for_input("Do you want to add errors? yes/no:") == "yes" else False
	"Should add rare events?"
	do_add_rare_event = True if prompt_for_input("Do you want to add a rare event? yes/no:") == "yes" else False

	if do_add_errors:
		show_error_menu(lattice_of_sensors, random_generator)

	if do_add_rare_event:
		show_rare_event_menu(lattice_of_sensors, random_generator)

	if not do_add_errors and not do_add_rare_event:
		create_error_free_data(lattice_of_sensors)

def main():

	if len(sys.argv) >= 2:
		run_id = str(sys.argv[1])
		file_of_time_series = str(sys.argv[2])

	print "Do you want to use interactive mode? yes/no:",
	should_use_interactive_mode = True if raw_input() == "yes" else False

	random_generator = random.Random()

	if should_use_interactive_mode:
		show_main_menu(random_generator)

if __name__ == "__main__":
	main()