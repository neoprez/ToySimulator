def normalize_to_range(time_series, desired_max=100):
	"""
	This function normalizes the data in time series to fall into the 
	desired range, between desired_min and desired_max.
	"""
	min_number = min(time_series)
	max_number = max(time_series) 

	if min_number == max_number:
		return [0] * len(time_series)
	else:
		min_coef = - min_number
		max_coef = desired_max / (max_number + min_coef * 1.0)
		return [(curr_number + min_coef) * max_coef for curr_number in time_series]

def merge_series(list_of_time_series, list_of_weights):
	"""
	This function merges a list of series into one according to their weight.
	"""
	merged_series = [0] * len(list_of_time_series[0])

	for idx in range(len(list_of_time_series)):
		coefficient_of_multiplication = list_of_weights[idx]
		series = list_of_time_series[idx]
		for index in range(len(series)):
			merged_series[index] = merged_series[index] + \
			(float(series[index]) * coefficient_of_multiplication)
	return merged_series