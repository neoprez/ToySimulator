import sensor
import graph

class Station(object):
	"""
	Station that holds multiple sensors
	"""
	def __init__(self, mean, sd, station_name, ran_gen):
		self.mean = mean
		self.sd = sd
		self.ran_gen = ran_gen
		self.station_name = station_name
		self.sensors_list = graph.Graph()

	def make_sensor(self, sensor_id, sensor_sd, type_of_sensor="NA"):
		sensor_mean = self.ran_gen.normalvariate(self.mean, self.sd)
		return sensor.Sensor(sensor_mean, sensor_sd, sensor_id, 
			self.ran_gen, type_of_sensor)

	def add_sensor_to_station(self, sensor_id, sensor_sd, type_of_sensor="NA"):
		"""
		Adds a sensor to the station that connects from node a to node b.
		If no sensor is on the station, then it is set as the main node.
		"""
		new_sensor = self.make_sensor(sensor_id, sensor_sd, type_of_sensor)
		self.sensors_list.addVertex(sensor_id, new_sensor)

	def connect_sensors(self, incomming_sensor, receiving_sensor, distance=0):
		"""
		Creates a connection between two sensors. The incomming_sensor sensor is the
		one that sends the signal to the receiving_sensor.
		Distance for later release. Will tell how far is the sensor and based on that
		we will determine the update frequency in time.
		"""
		self.sensors_list.addEdge(incomming_sensor, receiving_sensor, distance)

	def get_reading_from_all_sensors_in_station(self, number_of_readings_per_sensor):
		""" Returns the readings of alll sensors in the station """
		def get_time_series(sens):
			" pulls sensor for how many readings is going to do "
			return [sens.get_reading() for _ in range(number_of_readings_per_sensor)]

		return[get_time_series(sens.getNode()) for sens in self.sensors_list]

	def get_all_sensors_in_station(self):
		return self.sensors_list.getVertices()

	def get_sensor_in_station(self, key):
		return self.sensors_list.getVertex(key).getNode()

	def get_station_name(self):
		return self.station_name

	def __str__(self):
		return "Station " + self.station_name + "\nMean: " + str(self.mean) + \
		"\nSd: " + str(self.sd) + "\nNumber of sensors: " + \
		str(self.sensors_list.getNumVertices()) + "\n"


