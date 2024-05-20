# dashgo_simulations
Dashgo Simulation in URDF &amp; Gazebo

Update ver 5:
---
https://github.com/AIR-Hust/dashgo_simulations

Phiên bản 3 của Robot gồm:
---
- Đế Robot, 2 bánh xe, thân Robot và Lidar
- Tách riêng description và gazebo

Hướng dẫn sử dụng:
---
$ cd dashgo_ws/src/dashgo

$ sudo rm -r dashgo_description

$ git clone https://github.com/AIR-Hust/dashgo_simulations

$ cd ~/dashgo_ws

$ catkin_make

$ source devel/setup.bash

Để chạy description:
---
roslaunch dashgo_description dashgo_description.launch


Hướng dẫn Gmapping với giả lập:
---

Chạy dashgo_world trên Gazebo:
---
roslaunch dashgo_gazebo dashgo_gazebo.launch

Các world khác: 
- dashgo_house.launch
- world_stage_1.launch
- world_stage_2.launch
- world_stage_3.launch
- world_stage_4.launch

Chạy Gmapping:
---
roslaunch dashgo_gazebo gmapping.launch

Chạy Rviz:
---
roslaunch dashgo_rviz view_navigation.launch

Chạy teleop_keyboard:
---
rosrun dashgo_tools teleop_twist_keyboard.py

Lưu bản đồ:
---
rosrun map_server map_saver -f ~/dashgo_ws/map

Hướng dẫn Navigation với giả lập:
---

Chạy dashgo_world trên Gazebo:
---
roslaunch dashgo_gazebo dashgo_gazebo.launch

Chạy Navigation:
---
roslaunch dashgo_gazebo navigation.launch map_file:=$HOME/dashgo_ws/map.yaml

Chạy Rviz:
---
roslaunch dashgo_rviz view_navigation.launch
