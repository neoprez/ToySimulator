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



probability_of_erroneous_reading = 0.05
erroneous_reading_standard_deviation = 20

time_series = generate_time_series(1000)
time_series_b = generate_time_series(1000)
time_series_c = generate_time_series(1000)
normalized_time_series = normalize_to_range(time_series)
normalized_time_series_b = normalize_to_range(time_series_b)
normalized_time_series_c = normalize_to_range(time_series_c)

merged_series = merge_series([normalized_time_series, normalized_time_series_b, 
	normalized_time_series_c], [0, 0, 1])

list_of_time_series = [ time_series, time_series_b, time_series_c]
lattice_of_sensors = create_lattice_of_sensors(100, list_of_time_series)

erroneous_data = []
data_no_errors = []
for group_of_sensors in lattice_of_sensors:
	for sensor in group_of_sensors:
		sensor_data = sensor.get_time_series()
		data_no_errors.append(sensor_data)
		add_erroneous_reading_to_time_series(sensor_data, probability_of_erroneous_reading,
			erroneous_reading_standard_deviation)
		erroneous_data.append(sensor_data)

save_data_to_file(data_no_errors, "data_no_errors.csv")
save_data_to_file(erroneous_data, "erroneous_data.csv")


"""

normalized_merged_series = normalize_to_range(merged_series)

figure = plt.figure()

width = 1
height = 4

series_a_axes = figure.add_subplot(height, width, 1)
series_a_axes.plot(normalized_time_series)

series_b_axes = figure.add_subplot(height, width, 2)
series_b_axes.plot(normalized_time_series_b)

series_b_axes = figure.add_subplot(height, width, 3)
series_b_axes.plot(normalized_time_series_c)

merged_series_axes = figure.add_subplot(height, width, 4)
merged_series_axes.plot(normalized_merged_series)

plt.show()
"""