"""
This is the project
"""
import random
import csv
import station as st
import matplotlib.pyplot as plt

#random generator, uses seeds for testing purposes if you want repeatability
random_generator = random.Random(1) 
#error parameters
probability_of_erroneous_reading = 0.05
erroneous_reading_standard_deviation = 20
number_of_continous_erroneous_readings = 5

#sensor parameters
number_of_sensors_per_station = 1
number_of_readings = 10
actual_temperature = 20
sensor_standard_deviation = 2
station_standard_deviation = 2
global_temperature = 20
list_of_station_shifts = [10, -7, 2]

def save_data_to_file(data, file_name):
	with open(file_name, 'wb') as csv_file:
		csv_writer = csv.writer(csv_file)
		for time_series in data:
			csv_writer.writerow(time_series)
"""
def generate_error_free_data(number_of_sensors_per_station, number_of_readings, actual_temperature, 
	sensor_standard_deviation, list_of_station_shifts, global_temperature, 
	station_standard_deviation,random_generator):
	"Generates data"
	list_of_stations_temperatures = [global_temperature + station_shift
	 	for station_shift in list_of_station_shifts]

	list_of_stations = [st.Station(temperature, station_standard_deviation, random_generator) 
		for temperature in list_of_stations_temperatures]

	list_of_sensors = [station.get_sensor(sensor_standard_deviation) for station in list_of_stations
		for _ in range(number_of_sensors_per_station)]

	return [get_time_series(sensor, number_of_readings) 
		for sensor in list_of_sensors]
"""
def generate_error_free_data(hub, number_of_readings):
	"Generates error free data from each station"
	#get reading from all sensors in station
	def get_data_from_station(stat):
		return stat.get_reading_from_all_sensors_in_station(number_of_readings)

	return [get_data_from_station(hub[stat]) for stat in hub]

def add_erroneous_readings_to_data(data, probability_of_erroneous_reading, 
	erroneous_reading_standard_deviation, random_generator):
	def get_erroneous_value(value):
		return random_generator.normalvariate(value, erroneous_reading_standard_deviation)

	def get_value_with_probabilistics_erroneous_value(value):
		if random_generator.random() < probability_of_erroneous_reading:
			return get_erroneous_value(value)
		return value

	return [[get_value_with_probabilistics_erroneous_value(value) for value in time_series] 
		for time_series in data]

def add_erroneous_continuous_sequence_to_data(data, probability_of_erroneous_reading, 
	number_of_continous_erroneous_readings, random_generator):
	"""
	This function produces a continous sequence of erroneous readings. 
	Ex: 34, 35,35,35, 32, 38 ...
	"""
	def does_continous_erroneous_value_starts():
		return random_generator.random() < probability_of_erroneous_reading

	def add_index_repeat_value(time_series, start_index):
		end_index = min(start_index+number_of_continous_erroneous_readings, 
			len(time_series))
		for i in range(start_index, end_index):
			time_series[i] = time_series[start_index]

		return time_series

	revised_data = []

	for time_series in data:
		modified_time_series = time_series[:]
		for index in range(len(modified_time_series)):
			if does_continous_erroneous_value_starts():
				#repeat the sequence
				modified_time_series = add_index_repeat_value(modified_time_series, index)
		revised_data.append(modified_time_series)
	
	return revised_data

def main():
	"""
	data = generate_error_free_data(number_of_sensors_per_station, number_of_readings, 
	actual_temperature, sensor_standard_deviation, list_of_station_shifts, global_temperature, 
	station_standard_deviation,random_generator)
	save_data_to_file(data, "data.csv")
	plt.plot(data)
	plt.grid()
	plt.show()
	"""
	station_names = ["A", "B", "C"]
	main_hub = {}

	station_a = st.Station(global_temperature + list_of_station_shifts[0], 
		station_standard_deviation, station_names[0], random_generator)

	station_a.add_sensor_to_station("A", sensor_standard_deviation)
	station_a.add_sensor_to_station("B", sensor_standard_deviation)
	station_a.add_sensor_to_station("C", sensor_standard_deviation)
	station_a.add_sensor_to_station("D", sensor_standard_deviation)
	station_a.add_sensor_to_station("E", sensor_standard_deviation)

	station_a.connect_sensors("E", "D")
	station_a.connect_sensors("E", "C")
	station_a.connect_sensors("D", "B")
	station_a.connect_sensors("D", "C")
	station_a.connect_sensors("B", "A")
	station_a.connect_sensors("C", "A")

	station_b = st.Station(global_temperature + list_of_station_shifts[1], 
		station_standard_deviation, station_names[1], random_generator)

	station_b.add_sensor_to_station("A", sensor_standard_deviation)
	station_b.add_sensor_to_station("B", sensor_standard_deviation)
	station_b.add_sensor_to_station("C", sensor_standard_deviation)
	station_b.add_sensor_to_station("D", sensor_standard_deviation)
	station_b.add_sensor_to_station("E", sensor_standard_deviation)

	station_b.connect_sensors("E", "D")
	station_b.connect_sensors("E", "C")
	station_b.connect_sensors("D", "B")
	station_b.connect_sensors("C", "B")
	station_b.connect_sensors("C", "A")
	station_b.connect_sensors("B", "A")

	station_c = st.Station(global_temperature + list_of_station_shifts[2], 
		station_standard_deviation, station_names[2], random_generator)

	station_c.add_sensor_to_station("A", sensor_standard_deviation)
	station_c.add_sensor_to_station("B", sensor_standard_deviation)
	station_c.add_sensor_to_station("C", sensor_standard_deviation)
	station_c.add_sensor_to_station("D", sensor_standard_deviation)
	station_c.add_sensor_to_station("E", sensor_standard_deviation)

	station_c.connect_sensors("E", "C")
	station_c.connect_sensors("D", "E")
	station_c.connect_sensors("D", "C")
	station_c.connect_sensors("C", "B")
	station_c.connect_sensors("C", "A")
	station_c.connect_sensors("B", "A")

	main_hub[station_names[0]] = station_a
	main_hub[station_names[1]] = station_b
	main_hub[station_names[2]] = station_c

	data = generate_error_free_data(main_hub, number_of_readings)
	save_data_to_file(data, "data.csv")

main()

"""
data_with_erroneous_continous_sequence = add_erroneous_continuous_sequence_to_data(data, probability_of_erroneous_reading, 
	number_of_continous_erroneous_readings, random_generator)
save_data_to_file(data_with_erroneous_continous_sequence, "data_with_continous_errors.csv")

data_with_erroneous_reading = add_erroneous_readings_to_data(data, probability_of_erroneous_reading, 
	erroneous_reading_standard_deviation, random_generator)

save_data_to_file(data_with_erroneous_reading, "data_with_errors.csv")
"""