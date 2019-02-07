#!/usr/bin/python
import numpy as np
from sklearn.svm import SVC, OneClassSVM

import rospy
from sensor_msgs.msg import Imu
from std_msgs.msg import Bool,String
from fusion_msgs.msg import sensorFusionMsg

class SVMObserver:
    def __init__(self):
        rospy.init_node('svm_imu_test')
        rospy.Subscriber('/android/imu', Imu, self.imuCB)
        rospy.Subscriber('mode', Bool, self.modeCB)
        self.event_publisher = rospy.Publisher("/collisions_0", sensorFusionMsg, queue_size=10)

        self.is_training = True
        self.clf = OneClassSVM(nu=0.5, kernel="poly", gamma=0.1)
        rospy.spin()

    def modeCB(self,msg):
        self.is_training = msg.data

    def imuCB(self,msg):

        X = np.array([[msg.linear_acceleration.x, msg.linear_acceleration.y,
                       msg.angular_velocity.z]])

        if self.is_training:
            self.clf.fit(X)

        else:
	    fb_msg = sensorFusionMsg()
            fb_msg.sensor_id.data = "sv_detector"
	    fb_msg.data = X.flatten()

	    detected_class = self.clf.predict(X)

	    if detected_class > 0:
                rospy.logwarn('Event Detected')
                fb_msg.msg = sensorFusionMsg.WARN

            else:
                fb_msg.msg = sensorFusionMsg.OK

            self.event_publisher.publish(fb_msg)


if __name__ == '__main__':
    SVMObserver()