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
	

def generate_rare_event_to_lattice(lattice_of_sensors, max_dist, min_hearable_volume, 
	loudness, rare_event_song):
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
		new_series = normalize_to_range(new_series)
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
		 		sensor = lattice_of_sensors[r][c]
		 		if not (r != row_of_first_ocurrence and c != col_of_first_ocurrence):
		 			change_sensor_time_series_to_rare_series(sensor, loudness_of_the_area)

	#pick a random sensor
	row_of_first_ocurrence, col_of_first_ocurrence = get_a_random_sensor_index()
	sensor = lattice_of_sensors[row_of_first_ocurrence][col_of_first_ocurrence]
	change_sensor_time_series_to_rare_series(sensor, loudness)

	for current_distance in range(1, max_dist + 1):
		add_loudness_to_sensors_at_a_distance(current_distance, row_of_first_ocurrence, 
			col_of_first_ocurrence)




number_of_continous_erroneous_readings = 50
probability_of_erroneous_reading = 0.01
erroneous_reading_standard_deviation = 20
number_of_erroneous_points = 10
number_of_time_points = 1000

time_series = generate_time_series(number_of_time_points)
time_series_b = generate_time_series(number_of_time_points)
time_series_c = generate_time_series(number_of_time_points)
normalized_time_series = normalize_to_range(time_series)
normalized_time_series_b = normalize_to_range(time_series_b)
normalized_time_series_c = normalize_to_range(time_series_c)
"""
merged_series = merge_series([normalized_time_series, normalized_time_series_b, 
	normalized_time_series_c], [0, 0, 1])
"""
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
"""
add_erroneous_reading_to_sensor(sensor_0, probability_of_erroneous_reading, 
	erroneous_reading_standard_deviation)
add_erroneous_drift_towards_a_value_to_sensor(sensor_1, probability_of_erroneous_reading,
	number_of_erroneous_points)
add_continous_erroneous_reading_to_sensor(sensor_2, probability_of_erroneous_reading,
	number_of_continous_erroneous_readings)
"""
erroneous_data = gather_time_series_from_sensors(lattice_of_sensors)

"The rare event part"
max_dist = 1
min_hearable_volume = 0.1
loudness = 0.9
rare_event_song = generate_time_series(number_of_time_points)
rare_event_song = normalize_to_range(rare_event_song)
generate_rare_event_to_lattice(lattice_of_sensors, max_dist, min_hearable_volume, loudness,
 rare_event_song)

height = 3
figure = plt.figure()
axes_no_errors = figure.add_subplot(height, 1, 1)
axes_no_errors.set_title("Data no errors")
transposed_data = map(list, zip(*data_no_errors)) #to transpose the data
axes_no_errors.plot(transposed_data)
axes_no_errors.legend(range(0, dimension_of_lattice * dimension_of_lattice))

rare_data = gather_time_series_from_sensors(lattice_of_sensors)
axes_rare = figure.add_subplot(height, 1, 2)
axes_rare.set_title("Rare events")
transposed_data = map(list, zip(*rare_data))
axes_rare.plot(transposed_data)
axes_rare.legend(range(0, dimension_of_lattice * dimension_of_lattice))

axes_rare_song = figure.add_subplot(height, 1, 3)
axes_rare_song.set_title("Rare song")
axes_rare_song.plot(rare_event_song)
"""
axes_errors = figure.add_subplot(height, 1, 2)
axes_errors.set_title("Data with errors")
transposed_data = map(list, zip(*erroneous_data)) #to transpose the data
axes_errors.plot(transposed_data)
"""
plt.show()