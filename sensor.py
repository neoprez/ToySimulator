class Sensor(object):
	"""
	Represents a sensor and can be polled for data
	"""
	def __init__(self, time_series):
		self.time_series = time_series

	def get_time_series(self):
		return self.time_series

	def set_time_series(self, time_series):
		self.time_series = time_series