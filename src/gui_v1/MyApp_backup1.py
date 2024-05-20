#!/usr/bin/env python
# -*- coding: utf-8 -*-
# MyApp.py
# NV Huy
# 11_1_2019

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QMessageBox
import rospy
import rospkg
import sys, os
import yaml
from sensor_msgs.msg import Image as ImageMsg
from move_base_msgs.msg import MoveBaseActionResult
from form_v2 import Ui_Form
from model import Model 
from GoToPose import GoToPose
from playsound import playsound

# current_directory = os.getcwd() #Chi dung khi chay python binh thuong
current_directory = rospkg.RosPack().get_path('robot_test')
with open(current_directory + "/robotGUI_v1/data/GoalsData.yaml", 'r') as stream:
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
        self.navigator = GoToPose()
        self.index = 0

    def setupUI(self, MW):
        '''Setup UI cua lop cha (super class), va them code nay de dien ta cach ma chung ta muon UI hoat dong'''
        super(MainWindowUIClass, self).setupUi(MW)
        for obj in goal_data:
            self.comboBox_GoalSelect.addItem(obj['Name'])
        # self.label_statusbar.setText(_translate("Form","msg"))

    def statusPrint(self, msg):
        ''' In tin nhan trang thai vao o trang thai o goc duoi ben trai man hinh
        '''
        self.label_statusbar.setText(msg)

    def goAndTalk(self, obj, waitReturn):
        self.label_nextGoal.setText(obj['Name'])
        success = self.navigator.goto(obj['position'], obj['quaternion'],waitReturn)
        if success:
            try:
                audio_path = current_directory + '/Voice/' + obj['Audio']
                rospy.loginfo('playsound')
                playsound(audio_path)
            except Exception as e:
                rospy.loginfo(e) 
            self.label_currentGoal.setText(obj['Name'])    


    def update_background_color(self):
        '''Ham nay dung de thay doi mau nen cua nut bam Bat dau va Ket thuc khi enable va disable
        '''
        pass

    # slot
    def click_StartTour(self):
        '''Duoc goi khi nguoi dung nhan nut Bat dau trong Tour tu dong'''
        self.statusPrint(" Bat dau button pressed")
        # self.pushButton_StartTour.setEnabled(False)
        # self.pushButton_EndTour.setEnabled(True)
        for obj in goal_data:
            self.goAndTalk(obj,1)
    # slot
    def click_EndTour(self):
        '''Duoc goi khi nguoi dung nhan nut Bat dau trong Tour tu dong'''
        self.statusPrint(" Ket thuc button pressed")
        # self.pushButton_StartTour.setEnabled(True)
        # self.pushButton_EndTour.setEnabled(False)
    

    # slot
    def click_Go(self):
        '''Duoc goi khi nguoi dung nhan nut Bat dau trong Tour tu dong'''
        self.statusPrint(" Di button pressed")
        label = self.comboBox_GoalSelect.currentText()
        index = self.comboBox_GoalSelect.findText(label)
        self.label_nextGoal.setText(goal_data[index]['Name'])

        self.goAndTalk(goal_data[index], 1)
        self.index = index
    # slot
    def click_Cancel(self):
        '''Duoc goi khi nguoi dung nhan nut Bat dau trong Tour tu dong'''
        self.statusPrint(" Huy button pressed")

    # slot
    def click_Help(self):
        """Duoc goi khi nguoi dung nhan nut Bat dau trong Tour tu dong"""
        self.statusPrint(" Huong dan button pressed")
        with open(current_directory + '/data/user_help', 'r') as file:
            help_data = file.read()
        QMessageBox.about(QMessageBox(), 'Hướng dẫn', help_data)
        # QMessageBox.about("1","1")

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
            print e.message

    def callback(self, msg):
        # print type(msg)
        try:    
            image = QtGui.QImage(
                msg.data,
                msg.width,
                msg.height,
                msg.width * 3,
                QtGui.QImage.Format_RGB888
                )
            image = image.mirrored(1,0)
            self.label_CameraView.setPixmap(QtGui.QPixmap.fromImage(image)) #.fromImage    
        except:
            self.label_CameraView.setText("image camera")
        
def main():
    rospy.init_node('onboard_gui')
        
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QMainWindow()
    ui = MainWindowUIClass()
    ui.setupUI(Form)
    Form.show()

    rospy.Subscriber('/usb_cam/image_raw', ImageMsg, ui.callback)
    
    sys.exit(app.exec_())


main()
