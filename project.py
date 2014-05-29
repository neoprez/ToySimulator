"""
This is the project
"""
import random
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
	data = []
	for x in range(number_of_readings):
		data.append(sensor.get_reading())
	return data


s = Sensor(actual_temperature, sensor_standard_deviation, random_generator)
data = get_time_series(s, number_of_readings)
print data