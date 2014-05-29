"""
This is the project
"""
import random
import csv
#random generator, uses seeds for testing purposes if you want repeatability
random_generator = random.Random(1) 
number_of_sensors = 5
number_of_readings = 10
actual_temperature = 20
sensor_standard_deviation = 5

class Sensor(object):
	"""
	Represents a sensor and can be polled for data
	"""
	def __init__(self, mean, sd, ran_gen):
		self.mean = mean
		self.sd = sd
		self.ran_gen = ran_gen

	def get_reading(self):
		return self.ran_gen.normalvariate(self.mean, self.sd)

def get_time_series(sensor, number_of_readings):
	" pull sensor for how many readings is going to do "
	return [sensor.get_reading() for x in range(number_of_readings)]

def generate_data(number_of_sensors, number_of_readings, actual_temperature, 
	sensor_standard_deviation, random_generator):
	"Generates data"
	list_of_sensors = [Sensor(actual_temperature, sensor_standard_deviation, 
		random_generator) for _ in range(number_of_sensors)]
	return [get_time_series(sensor, number_of_readings) 
		for sensor in list_of_sensors]

def save_data_to_file(data, file_name):
	with open(file_name, 'wb') as csv_file:
		csv_writer = csv.writer(csv_file)
		for time_series in data:
			csv_writer.writerow(time_series)

data = generate_data(number_of_sensors, number_of_readings, actual_temperature, 
	sensor_standard_deviation, random_generator)

save_data_to_file(data, "data.csv")
