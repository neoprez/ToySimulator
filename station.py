import sensor

class Station(object):
	"""
	Station that holds multiple sensors
	"""
	def __init__(self, mean, sd, ran_gen):
		self.mean = mean
		self.sd = sd
		self.ran_gen = ran_gen

	def get_sensor(self, sensor_sd):
		sensor_mean = self.ran_gen.normalvariate(self.mean, self.sd)
		return sensor.Sensor(sensor_mean, sensor_sd, self.ran_gen)