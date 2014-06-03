class Sensor(object):
	"""
	Represents a sensor and can be polled for data
	"""
	def __init__(self, mean, sd, sensor_id, ran_gen, type_of_sensor="NA"):
		self.mean = mean
		self.sd = sd
		self.ran_gen = ran_gen
		self.sensor_id = sensor_id
		self.online_status = 1	#to check the status of the sensor. 0 offline 1 online
		self.type_of_sensor = type_of_sensor

	def get_reading(self):
		return self.ran_gen.normalvariate(self.mean, self.sd)

	def get_online_status(self):
		return self.online_status

	def set_online_status(self, status):
		"""Use it to change the status of the sensor"""
		self.online_status = status

	def get_sensor_id(self):
		return self.sensor_id

	def __str__(self):
		return "Sensor " + self.sensor_id + ":\nType of sensor: " + \
		str(self.type_of_sensor) + "\nMean: " + str(self.mean) + \
		"\nSd: " + str(self.sd) + "\nStatus: " + str(self.online_status)