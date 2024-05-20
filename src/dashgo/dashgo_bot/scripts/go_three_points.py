#!/usr/bin/env python
import rospy
from go_to_a_point_on_the_map import GoToPose
if __name__ == '__main__':
    try:
        rospy.init_node('nav_test', anonymous=False)
        navigator = GoToPose()

        # Point 1
        position1 = {'x': 1, 'y' : 1.5}
        quaternion1 = {'r1' : 0.000, 'r2' : 0.000, 'r3' : 0.000, 'r4' : 1.000}

        rospy.loginfo("Go to (%s, %s) pose", position1['x'], position1['y'])
        success = navigator.goto(position1, quaternion1)

        if success:
            rospy.loginfo("Reached the desired pose")
        else:
            rospy.loginfo("The base failed to reach the desired pose")

        # Sleep to give the last log messages time to be sent
        rospy.sleep(1)
        # Point 2
        position2 = {'x': 0.163, 'y' : 0.001}
        quaternion2 = {'r1' : 0.000, 'r2' : 0.000, 'r3' : 0.000, 'r4' : 1.000}

        rospy.loginfo("Go to (%s, %s) pose", position2['x'], position2['y'])
        success = navigator.goto(position2, quaternion2)

        if success:
            rospy.loginfo("Reached the desired pose")
        else:
            rospy.loginfo("The base failed to reach the desired pose")

        # Sleep to give the last log messages time to be sent
        rospy.sleep(1)
        # Point 3
        position3 = {'x': -0.04, 'y' : -1.53}
        quaternion3 = {'r1' : 0.000, 'r2' : 0.000, 'r3' : 0.000, 'r4' : 1.000}

        rospy.loginfo("Go to (%s, %s) pose", position2['x'], position2['y'])
        success = navigator.goto(position3, quaternion3)

        if success:
            rospy.loginfo("Reached the desired pose")
        else:
            rospy.loginfo("The base failed to reach the desired pose")

        # Sleep to give the last log messages time to be sent
        rospy.sleep(1)          
    except rospy.ROSInterruptException:
        rospy.loginfo("Ctrl-C caught. Quitting")
