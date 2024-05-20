#!/usr/bin/env python
import rospy
import yaml
from go_to_a_point_on_the_map import GoToPose

if __name__ == '__main__':

    # Read information from yaml file
    with open("route.yaml",'r') as stream:
        dataMap = yaml.safe_load(stream)

    try:
        # Initialize
        rospy.init_node('follow_route', anonymous=False)
        navigator = GoToPose()
    
        for obj in dataMap:

            if rospy.is_shutdown():
                break

            name = obj['filename']

            # Navigation
            rospy.loginfo("Go to %s pose", name[:-4])
            success = navigator.goto(obj['position'], obj['quaternion'])
            if not success:
                rospy.loginfo("Failed to reach %s pose", name[:-4])
                continue
            rospy.loginfo("Reached %s pose", name[:-4])

    except rospy.ROSInterruptException:
        rospy.loginfo("Ctrl-C caught. Quitting")