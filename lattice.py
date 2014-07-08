import sensor
import time_series_tools as tstools

class Lattice(object):
	"Represents a group of sensors that are correlated"
	def __init__(self, dimension_of_lattice):
		self.dimension_of_lattice = dimension_of_lattice
		self.number_of_sensors = dimension_of_lattice**2
		self.lattice = [] #a group of sensors
		self.initialize_sensor_grid()

	def initialize_sensor_grid(self):
		"Initializes the grid of sensors with an empty time series"
		for _ in range(self.dimension_of_lattice):
			row_of_sensors = []
			for _ in range(self.dimension_of_lattice):
				row_of_sensors.append(sensor.Sensor([]))
			self.lattice.append(row_of_sensors)

	def set_time_series_according_to_sensor_weight(self, list_of_time_series):
		"""
		Sets the time series of a sensor depending on the location of the grid.
		It normalizes the data so it falls betweem 0 and 1 for the neural network.
		"""
		lattice_of_sensors = []

		for row in range(self.dimension_of_lattice):
			for col in range(self.dimension_of_lattice):

				weigth_from_b = row / (self.dimension_of_lattice * 1.0) #in vertical increase b 
				weigth_from_a = col / (self.dimension_of_lattice * 1.0) #in horizontal increase a
				weight_from_c = 0
				total_weight = weigth_from_a + weigth_from_b

				if total_weight < 1:
					weight_from_c = 1 - total_weight

				list_of_weights = [weigth_from_a, weigth_from_b, weight_from_c]
				time_series_for_sensor = \
				tstools.merge_series(list_of_time_series, list_of_weights)
				time_series_for_sensor = \
				tstools.normalize_to_range(time_series_for_sensor, 1)
				self.set_sensor_time_series(row, col, time_series_for_sensor)

	def set_sensor_time_series(self, row, col, time_series):
		self.lattice[row][col].set_time_series(time_series)

	def get_sensor(self, row, col):
		return self.lattice[row][col]

	def gather_time_series_from_all_sensors(self):
		"""
		This function collects the time series from the sensors in the lattice.
		"""
		collection_of_time_series = []
		for group_of_sensors in self.lattice:
			for sensor in group_of_sensors:
				sensor_data = sensor.get_time_series()
				collection_of_time_series.append(sensor_data)
		return collection_of_time_series

