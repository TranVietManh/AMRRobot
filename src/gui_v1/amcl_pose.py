import rospy
from geometry_msgs.msg import PoseWithCovarianceStamped

def poseAMCLCallback(data):
	rospy.loginfo("The amcl infor:")
	rospy.loginfo(data.pose.pose.position.x)
	rospy.loginfo(data.pose.pose.position.y)
	rospy.loginfo(data.pose.pose.orientation.w)

if __name__ == '__main__':
	print("Start")
	rospy.init_node('receiver',anonymous=True)
	rospy.Subscriber('/amcl_pose',PoseWithCovarianceStamped,poseAMCLCallback)
	rospy.spin()


