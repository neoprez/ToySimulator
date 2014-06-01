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