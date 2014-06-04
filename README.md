#Toy Simulator 2014

Authors:
Rodny Perez
Emily Dolson
Josh Nahum

This projects aims to develop a simulator for wireless sensors.

We will something else later

##Todo
- Implementing features:
	* Sensor dependancy (Done)
	* Time occilation (The mean changes over time) (Done)
	* Days or seasons (comming soon)
	* Sensors that varies in mean and standard deviation
	* Sensor pattern
	* Partition sensors by groups (Done)
	* Multiple sensor type (Done)
	* Temperature drifts globally

##Errors and anomalies
- Abrupt changes (added)
- Large deviation 
- Unusually low variance (change in result from predicted value)
- Deviation from neighbors (variance in result from neigbors)
- Drift towards a particular value (0 or something else) (change over time in unforeseen ways)
- increasingly mean difference

##Ways of representing anomalies
- Change in mean value among multiple sensors. Either within a group or an entire field
- Adjusting the correlation between sensor modalities