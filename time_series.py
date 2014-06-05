import random
import matplotlib.pyplot as plt
import sensor
import csv

random_generator = random.Random()

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

def normalize_to_range(time_series, desired_max=100):
	"""
	This function normalizes the data in time series to fall into the 
	desired range, between desired_min and desired_max.
	"""
	min_number = min(time_series)
	max_number = max(time_series) 

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
			time_series_for_sensor = normalize_to_range(time_series_for_sensor)
			list_of_sensors.append(sensor.Sensor(time_series_for_sensor))
		lattice_of_sensors.append(list_of_sensors)

	return lattice_of_sensors


def save_data_to_file(data, file_name):
	with open(file_name, 'wb') as csv_file:
		csv_writer = csv.writer(csv_file)
		for time_series in data:
			csv_writer.writerow(time_series)

def add_erroneous_reading_to_time_series(time_series, probability_of_erroneous_reading, 
	erroneous_reading_standard_deviation):
	def get_erroneous_value(value):
		return random_generator.normalvariate(value, erroneous_reading_standard_deviation)

	def get_value_with_probabilistics_erroneous_value(value):
		if random_generator.random() < probability_of_erroneous_reading:
			return get_erroneous_value(value)
		return value

	return [get_value_with_probabilistics_erroneous_value(value) for value in time_series]

def add_erroneous_continuous_sequence_to_time_series(time_series, probability_of_erroneous_reading, 
	number_of_continous_erroneous_readings):
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
	number_of_erroneous_points):
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
	number_of_continous_erroneous_readings):
	"""
	This function adds a sequence erroneous readings to a single sensor time series. 
	This function modifies the sensor's original time series.
	"""
	time_series = sensor.get_time_series()
	erroneous_reading = add_erroneous_continuous_sequence_to_time_series(time_series, 
		probability_of_erroneous_reading, number_of_continous_erroneous_readings)
	sensor.set_time_series(erroneous_reading)

def add_erroneous_reading_to_sensor(sensor, probability_of_erroneous_reading, 
	erroneous_reading_standard_deviation):
	"""
	This function adds erroneous readings to a single sensor time series. 
	This function modifies the sensor's original time series.
	"""
	time_series = sensor.get_time_series()
	erroneous_reading = add_erroneous_reading_to_time_series(time_series, 
		probability_of_erroneous_reading, erroneous_reading_standard_deviation)
	sensor.set_time_series(erroneous_reading)

def add_erroneous_drift_towards_a_value_to_sensor(sensor, probability_of_erroneous_reading, 
	number_of_erroneous_points):
	"""
	This function adds erroneous drift to a single sensor time series. 
	This function modifies the sensor's original time series.
	"""
	time_series = sensor.get_time_series()
	erroneous_reading = add_erroneous_drift_towards_a_value(time_series, 
		probability_of_erroneous_reading, number_of_erroneous_points)
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
	

number_of_continous_erroneous_readings = 50
probability_of_erroneous_reading = 0.01
erroneous_reading_standard_deviation = 20
number_of_erroneous_points = 10

time_series = generate_time_series(1000)
time_series_b = generate_time_series(1000)
time_series_c = generate_time_series(1000)
normalized_time_series = normalize_to_range(time_series)
normalized_time_series_b = normalize_to_range(time_series_b)
normalized_time_series_c = normalize_to_range(time_series_c)

merged_series = merge_series([normalized_time_series, normalized_time_series_b, 
	normalized_time_series_c], [0, 0, 1])

dimension_of_lattice = 2
list_of_time_series = [normalized_time_series, normalized_time_series_b, normalized_time_series_c]
lattice_of_sensors = create_lattice_of_sensors(dimension_of_lattice, list_of_time_series)


continous_errors = []
drifted_data = []
data_no_errors = gather_time_series_from_sensors(lattice_of_sensors)

lattice_row_1 = lattice_of_sensors[0]
lattice_row_2 = lattice_of_sensors[1]

sensor_0 = lattice_row_1[0]
sensor_1 = lattice_row_1[1]
sensor_2 = lattice_row_2[1]

add_erroneous_reading_to_sensor(sensor_0, probability_of_erroneous_reading, 
	erroneous_reading_standard_deviation)
add_erroneous_drift_towards_a_value_to_sensor(sensor_1, probability_of_erroneous_reading,
	number_of_erroneous_points)
add_continous_erroneous_reading_to_sensor(sensor_2, probability_of_erroneous_reading,
	number_of_continous_erroneous_readings)

erroneous_data = gather_time_series_from_sensors(lattice_of_sensors)

height = 2
figure = plt.figure()
axes_no_errors = figure.add_subplot(height, 1, 1)
axes_no_errors.set_title("Data no errors")
transposed_data = map(list, zip(*data_no_errors)) #to transpose the data
axes_no_errors.plot(transposed_data)

"""
axes_c = figure.add_subplot(3, 1, 2)
axes_c.set_title("time_series_c")
#transposed_data = map(list, zip(*time_series)) #to transpose the data
axes_c.plot(normalized_time_series_c)

axes_drifted = figure.add_subplot(3, 1, 3)
axes_drifted.set_title("drifted_data")
transposed_data = map(list, zip(*drifted_data)) #to transpose the data
axes_drifted.plot(transposed_data)
"""

axes_errors = figure.add_subplot(height, 1, 2)
axes_errors.set_title("Data with errors")
transposed_data = map(list, zip(*erroneous_data)) #to transpose the data
axes_errors.plot(transposed_data)
"""
axes_continous_errors = figure.add_subplot(3, 1, 3)
axes_continous_errors.set_title("Data with continous errors")
transposed_data = map(list, zip(*continous_errors)) #to transpose the data
axes_continous_errors.plot(transposed_data)
"""

plt.show()