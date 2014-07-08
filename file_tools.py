"This class is used to work over files"
import csv

def save_data_to_file(data, file_name, mode="wb"):
	with open(file_name, mode) as csv_file:
		csv_writer = csv.writer(csv_file)
		for time_series in data:
			csv_writer.writerow(time_series)

def get_data_from_file(file_name, mode="rb"):
	data = []
	with open(file_name, mode) as csv_file:
		csv_reader = csv.reader(csv_file)
		for row in csv_reader:
			data.append(row)
	return data
