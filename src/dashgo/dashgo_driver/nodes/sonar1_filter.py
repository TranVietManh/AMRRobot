#!usr/bin/env python
import rospy
from std_msgs.msg import Float64
from sensor_msgs.msg import Range

filter_length = 15
buffer_filter = [0.8] * filter_length
count_filter = 0
sum_data = 12

def sonar_callback(data):
	global buffer_filter
	global sum_data
	global count_filter
	sonar_data = data.range
	# rospy.loginfo(data.range)

	sum_data = sum_data + sonar_data -  buffer_filter[count_filter]
	buffer_filter[count_filter] = sonar_data
	filter_out = sum_data /filter_length
	rospy.loginfo(filter_out)
	# filter_out_msg = Float64()
	# filter_out_msg.data = filter_out
	# pub.publish(filter_out_msg)
	filtered_data = Range()
	filtered_data.header = data.header
	filtered_data.radiation_type = data.radiation_type
	filtered_data.field_of_view = data.field_of_view
	filtered_data.min_range = data.min_range
	filtered_data.max_range = data.max_range
	filtered_data.range = filter_out
	pub.publish(filtered_data)
	count_filter += 1
	if count_filter == filter_length:
		count_filter = 0

def listener():
	rospy.init_node('listener_sonar_1')
	rospy.Subscriber("/sonar1", Range, sonar_callback)

	global pub
	pub = rospy.Publisher("/sonar1_new", Range, queue_size = 10)

	rospy.spin()

if __name__ == '__main__':
	listener()