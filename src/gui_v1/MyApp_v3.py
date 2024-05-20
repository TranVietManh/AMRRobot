#!/usr/bin/env python
# -*- coding: utf-8 -*-
# MyApp.py
# NV Huy
# 13_02_2019
# Idea: Phan thuc thi lien quan den di chuyen, GUI chi thuc hien ghi vao file
# text, 1 chuong trinh thuc thi khac se lay du lieu tu file text de thuc thi:
# di chuyen, phat am thanh...

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QTimer, QThread, pyqtSlot
import rospy
import rospkg
import sys, os, threading
import yaml
from cv_bridge import CvBridge, CvBridgeError
from std_msgs.msg import String
from sensor_msgs.msg import Image as ImageMsg
from move_base_msgs.msg import MoveBaseActionResult
from form_v3 import Ui_Form
from model_v2 import Model, NewSignal
#from playsound import playsound
import cv2
current_directory = os.getcwd()+"/data/" #Chi dung khi chay python binh thuong
#current_directory = rospkg.RosPack().get_path('robot') + "/robotGUI_v1/data/"
with open(current_directory + "test.yaml", 'r') as stream:
    try:
        goal_data = yaml.load(stream)
        # print(yaml.load(stream))
    except yaml.YAMLError as exc:
        print(exc)

class MainWindowUIClass(Ui_Form):
    """docstring for MainWindowUIClass"""

    def __init__(self):
        """Khoi tao super class"""
        super(Ui_Form, self).__init__()
        self.model = Model()
        # Bien:
        self.model.goal_data = goal_data
        self.index = int
        self.GUIcmd = 0
        self.isTour = 0
        self.timedown = 0
        self.newSignal = NewSignal()
        self.newSignal.changed.connect(self.changed_timedelay)
        self.initTimer()
        # self.setWindowIcon(QtGui.QIcon(current_directory+"image/robot.ico"))

    def timeout(self):
        if self.timedown>=0:
            self.label_noticeTour.setText("Time remaining: " + str(self.timedown) + ". To Skip, press 'Tiếp tục' button.")
            self.timedown -= 1
        else:
            self.timer.stop()
            self.label_noticeTour.setText("Resumming tour...")
            self.go()

    def initTimer(self):
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.timeout)

    def startTimer(self):
        print("timer start..." + str(self.timedown))
        self.timer.start()

    # @pyqtSlot(int)
    def changed_timedelay(self,timeDelay):
        self.timedown = timeDelay
        self.startTimer()
        # print threading.currentThread().getName()


    def setupUI(self, MW):
        '''Setup UI cua lop cha (super class), va them code nay de dien ta cach ma chung ta muon UI hoat dong'''
        super(MainWindowUIClass, self).setupUi(MW)
        for obj in goal_data:
            self.comboBox_GoalSelect.addItem(obj['Name'])
        self.onActivated()

    def statusPrint(self, msg):
        ''' In tin nhan trang thai vao o trang thai o goc duoi ben trai man hinh
        '''
        self.label_statusbar.setText(msg)


    def go(self):
        try:
            print(self.model.goalsBuffer)
            self.label_noticeTour.setText("going...")
            self.statusPrint("")
            self.index = self.model.goalsBuffer[0]
            self.label_nextGoal.setText(goal_data[self.index]['Name'])
            self.model.goto(goal_data[self.index]['position'], goal_data[self.index]['quaternion'])
            self.GUIcmd = 1
        except Exception as e:
            print(e)

    # slot
    def click_StartTour(self):
        '''Duoc goi khi nguoi dung nhan nut Bat dau trong Tour tu dong'''
        self.statusPrint("Bat dau button pressed")
        self.pushButton_StartTour.setEnabled(False)
        self.pushButton_EndTour.setEnabled(True)
        self.pushButton_PauseTour.setEnabled(True)
        self.pushButton_ResumeTour.setEnabled(True)
        self.isTour = 1

        for obj in goal_data:
            self.model.goalsBuffer.append(obj['Index'])
        # print self.model.goalsBuffer
        self.go()

    #slot
    def click_PauseTour(self):
        self.statusPrint("Pause tour...")
        self.model.cancel(clear_buffer=False)
        # if self.model.goalsBuffer[0] != self.index:
        #     self.model.goalsBuffer.insert(0, self.index)
        print(self.model.goalsBuffer)

    #slot
    def click_ResumeTour(self):
        if self.timer.isActive():
            self.timer.stop()
            self.timedown = 0
            self.label_noticeTour.setText("Skip, Resumming Tour...")
        self.statusPrint("Resumming tour...")
        self.go()

    # slot
    def click_EndTour(self):
        '''Duoc goi khi nguoi dung nhan nut Bat dau trong Tour tu dong'''
        self.statusPrint(" Ket thuc button pressed")
        self.label_noticeTour.setText("")
        self.pushButton_StartTour.setEnabled(True)
        self.pushButton_EndTour.setEnabled(False)
        self.pushButton_PauseTour.setEnabled(False)
        self.pushButton_ResumeTour.setEnabled(False)
        self.model.cancel()
        self.GUIcmd = 0
        self.isTour = 0

    # slot
    def click_Go(self):
        '''Duoc goi khi nguoi dung nhan nut Bat dau trong Tour tu dong'''
        self.statusPrint(" Di button pressed")
        label = self.comboBox_GoalSelect.currentText()
        self.index = self.comboBox_GoalSelect.findText(label)
        self.model.goalsBuffer = [goal_data[self.index]['Index']]
        print(self.model.goalsBuffer)
        self.go()

    # slot
    def click_Cancel(self):
        '''Duoc goi khi nguoi dung nhan nut Bat dau trong Tour tu dong'''
        self.statusPrint(" Huy button pressed")
        self.model.cancel()
        self.GUIcmd = 0


    # slot
    def click_Help(self):
        """Duoc goi khi nguoi dung nhan nut Bat dau trong Tour tu dong"""
        self.statusPrint(" Huong dan button pressed")
        with open(current_directory + 'user_help', 'r') as file:
            help_data = file.read()
        QMessageBox.about(QMessageBox(), 'Hướng dẫn', help_data)
        # QMessageBox.about("1","1")


    def goalreached_callback(self, msg):
        rospy.loginfo('result status: ' + msg.status.text)
        if (msg.status.text == 'Goal reached.') & (self.GUIcmd == 1):
            # self.goalReached = 1
            self.statusPrint("goalReached!")
            self.label_currentGoal.setText(goal_data[self.index]['Name'])
            # Chay timer
            try:
                del self.model.goalsBuffer[0]
            except:
                pass
            if (self.isTour) & (len(self.model.goalsBuffer) != 0):
                self.label_nextGoal.setText(goal_data[self.model.goalsBuffer[0]]['Name'])
                timeDelay = goal_data[self.index]["TimeDelay"]
                self.newSignal.x = timeDelay
            else:
                self.label_noticeTour.setText("Finished tour.")
                self.label_nextGoal.setText("")
                self.pushButton_StartTour.setEnabled(True)
                self.pushButton_EndTour.setEnabled(False)
                self.pushButton_PauseTour.setEnabled(False)
                self.pushButton_ResumeTour.setEnabled(False)
                self.GUIcmd = 0
                self.isTour = 0
            # Phat am thanh
            try:
                audio_path = current_directory + '/Voice/' + goal_data[self.index]['Audio']
                rospy.loginfo('playsound')
                playsound(audio_path)
            except Exception as e:
                print(e)

    def onActivated(self):
        """
        Ham nay de cap nhat gia tri lua chọn ở combobox vào label_GoalDetail
        """
        try:
            label = self.comboBox_GoalSelect.currentText()
            index = self.comboBox_GoalSelect.findText(label)
            detail = goal_data[index]['Detail']
            self.label_GoalDetail.setText(detail)
        except Exception as e:
            print(e.message)

    def cam_callback(self, msg):
        # print type(msg)
        bridge = CvBridge()

        cv_image = bridge.imgmsg_to_cv2(msg, "rgb8")
        cv_image = cv2.resize(cv_image,(480,300))

        try:
            image = QtGui.QImage(
                cv_image,
                cv_image.shape[1],
                cv_image.shape[0],
                cv_image.shape[1] * 3,
                QtGui.QImage.Format_RGB888
                )

            image = image.mirrored(0,0)
            self.label_CameraView.setPixmap(QtGui.QPixmap.fromImage(image)) #.fromImage
        except:
            self.label_CameraView.setText("image camera")



def main():
    rospy.init_node('onboard_gui')
    # while not rospy.is_shutdown():
    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon(current_directory+"image/robot.ico"))
    Form = QtWidgets.QMainWindow()
    ui = MainWindowUIClass()
    ui.setupUI(Form)
    Form.show()

    cmd_pub = rospy.Publisher('command_publisher', String, queue_size=10)
    # camera thuong: /usb_cam/image_raw
    # trong gazebo: /camera/rgb/image_raw
    # rospy.Subscriber('/usb_cam/image_raw', ImageMsg, ui.cam_callback)   # normal camera no detection
    # to run detection install package dnn_detect "sudo apt install ros-kinetic-dnn-detect"
    # Running detection 1, rosrun usb_cam usb_cam_node
    #                   2, roslaunch dnn_detect dnn_detect.launch camera:=/usb_cam image:=image_raw
    rospy.Subscriber('/dnn_images', ImageMsg, ui.cam_callback)  # for detection with deeplearning
    rospy.Subscriber('/move_base/result',MoveBaseActionResult, ui.goalreached_callback)
    sys.exit(app.exec_())
    # rospy.on_shutdown(sys.exit(app.exe_()))
main()
