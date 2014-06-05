import random
import matplotlib.pyplot as plt

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




time_series = generate_time_series(1000)
normalized_time_series = normalize_to_range(time_series)

plt.plot(normalized_time_series)
plt.show()
