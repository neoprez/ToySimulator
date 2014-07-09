"""
This file will only generate the time series to a file
"""

import math
import sys
import file_tools as ft
import time_series_tools as tstools

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

def generate_predictable_time_series(number_of_time_points):
	"This retuns a predictable time series"
	return [x/100.0 for x in range(number_of_time_points)]

def generate_predictable_sin_time_series(number_of_time_points):
	return [math.sin(x/20.0) for x in range(number_of_time_points)]

def generate_predictable_parabola_time_series(number_of_time_points, shift=0):
	return [(x+shift)**2 for x in range(number_of_time_points)]


def main():
	number_of_time_points = 20000 #number of time points to generate
	time_series_header = ["Time series A", "Time series B", "Time series C"]
	run_id = ""

	if len(sys.argv) >= 2:
		run_id = str(sys.argv[1])

	#we are using a lattice of sensors that reads data from different
	#songs. We combine the listening from 3 different readings.
	time_series = generate_predictable_parabola_time_series(number_of_time_points)
	time_series_b = generate_predictable_time_series(number_of_time_points) #series b
	time_series_c = generate_predictable_parabola_time_series(number_of_time_points, 100) #series c, right shift by 100
	rare_event_song = generate_predictable_sin_time_series(number_of_time_points)

	data_to_write = [time_series, time_series_b, time_series_c]

	ft.save_data_to_file(data_to_write, "the_series_" + run_id + ".csv")
	ft.save_data_to_file([rare_event_song], "rare_song_" + run_id + ".csv")

	normalized_time_series = tstools.normalize_to_range(time_series)
	normalized_time_series_b = tstools.normalize_to_range(time_series_b)
	normalized_time_series_c = tstools.normalize_to_range(time_series_c)

	data_to_write = [normalized_time_series, normalized_time_series_b, normalized_time_series_c]
	ft.save_data_to_file(data_to_write, "the_series_normalized_" + run_id +".csv")

	rare_event_song_normalized = tstools.normalize_to_range(rare_event_song)
	ft.save_data_to_file([rare_event_song_normalized], "rare_song_normalized_" + run_id + ".csv")

main()