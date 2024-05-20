#include "ros/ros.h"
#include "serial/serial.h"
#include <string>
#include <cmath>
#include <geometry_msgs/Quaternion.h>
#include <sensor_msgs/Imu.h>
#include <std_msgs/String.h>
#include <std_msgs/Float32.h>
#include <std_srvs/Empty.h>
#include <tf/transform_broadcaster.h>
#include <tf/transform_datatypes.h>

using namespace std;

void init_imu(serial::Serial& ser,int& cfg_baud_rate_,int& cfg_freq_,bool enable_transfer)
{
    const char *cmd_packet="$MIB,RESET*87";
    size_t cmd_packet_len = strlen(cmd_packet);
    try
    {
        ROS_WARN("***start to init serial_port,and reset imu 0");
        ROS_WARN("***imu  is R6093U,baud is 38400");
        ser.write((const uint8_t*)(cmd_packet), cmd_packet_len);
    }
    catch(serial::IOException& e)
    {
        ROS_ERROR("init imu error");
    }
}

std::string string_to_hex(const std::string& input)
{
    static const char* const lut = "0123456789ABCDEF";
    size_t len = input.length();

    std::string output;
    output.reserve(2 * len);
    for (size_t i = 0; i < len; ++i)
    {
        const unsigned char c = input[i];
        output.push_back(lut[c >> 4]);
        output.push_back(lut[c & 15]);
    }
    return output;
}

int main(int argc, char**argv)
{
    ros::init(argc,argv,"pathgo_imu_node");
    ros::NodeHandle nh;
    serial::Serial ser;
    std::string port;
    int cfg_baud_rate_=38400;
    int cfg_freq_ = 0;
    bool enable_transfer = true;
    bool head_flag=false;
    ros::Time current_time, last_time;
    std::string imu_frame_id;
    ros::Duration dur_time;

    nh.param<std::string>("/pathgo_imu_node/port", port, "/dev/ttyUSB0");
    nh.param<int>("/pathgo_imu_node/imu_baudrate", cfg_baud_rate_, 115200);
    nh.param<int>("/pathgo_imu_node/imu_freq", cfg_freq_, 100);
    nh.param<std::string>("/pathgo_imu_node/imu_frame_id", imu_frame_id, "imu_base");

    ros::Publisher imu_angle_pub = nh.advertise<std_msgs::Float32>("imu_angle", 50);
    ros::Publisher imu_pub = nh.advertise<sensor_msgs::Imu>("imu", 50);

    ros::Rate r(1000);
    try
    {
        ser.setPort(port);
        ser.setBaudrate(38400);
        serial::Timeout to = serial::Timeout::simpleTimeout(1000);
        ser.setTimeout(to);
        ser.open();
    }
    catch(serial::IOException& e)
    {
        ROS_ERROR_STREAM("Unable to open serial port " << ser.getPort() << ". Trying again in 5 seconds.");
        ros::Duration(5).sleep();
    }
    //init imu is 0
    if(ser.isOpen())
    {
        init_imu(ser,cfg_baud_rate_,cfg_freq_,enable_transfer);
    }
    //read imu data
    current_time = ros::Time::now();
    last_time = ros::Time::now();
    while(ros::ok())
    {

        if(ser.isOpen()&&ser.available())
        {
            std::string input_0 = ser.read(1);
            std::string input_0_hex = string_to_hex(input_0);
            std::string rev_str;
            //cout<<"input_0_hex="<<input_0_hex<<endl;

            if(input_0_hex=="A6")
            {
                std::string input_1 = ser.read(1);
                std::string input_1_hex = string_to_hex(input_1);
                //cout<<"input_1_hex="<<input_1_hex<<endl;
                if(input_1_hex=="A6")
                {
                    std::string one_other = ser.read(26-2);
                    std::string one_other_hex = string_to_hex(one_other);
                    rev_str=input_0+input_1+one_other;
                    std::string rev_str_hex=input_0_hex+input_1_hex+one_other_hex;
                    //cout<<"one_str= "<<rev_str_hex<<endl;
                }
            } //end "A6"

            char *chr = &rev_str[0u];
            /*
            for(int i=0;i<26;i++)
            {
                std::string output_str;
                output_str=chr[i];
                cout<<string_to_hex(output_str)<<endl;
            }*/
            short angle_yaw = ((chr[7] & 0xFF) | ((chr[8] << 8) & 0XFF00));
            short angleRate_z = ((chr[13] & 0xFF) | ((chr[14] << 8) & 0XFF00));
            short int acc_x = ((chr[15] & 0xFF) | ((chr[16] << 8) & 0XFF00));
            short int acc_y = ((chr[17] & 0xFF) | ((chr[18] << 8) & 0XFF00));
            short int acc_z = ((chr[19] & 0xFF) | ((chr[20] << 8) & 0XFF00));
            //cout<<"angle_yaw="<<angle_yaw<<", angleRate_z="<<angleRate_z<<", acc_x="<<
            //     acc_x<<", acc_y="<<acc_y<<", acc_z="<<acc_z<<endl;

            current_time = ros::Time::now();
            dur_time = current_time - last_time;

            std_msgs::Float32 imu_angle_mgs;
            imu_angle_mgs.data = (double)(-1*angle_yaw/100.f);
            imu_angle_pub.publish(imu_angle_mgs);

            sensor_msgs::Imu imu;
            imu.header.stamp = ros::Time::now();
            imu.header.frame_id = imu_frame_id;
            //通过yaw角度转成四元数
            tf::Quaternion orientation = tf::createQuaternionFromYaw((double)-1*angle_yaw*3.14/(180*100));
            //tf::Quaternion differential_rotation;
            quaternionTFToMsg(orientation, imu.orientation);
            imu.orientation_covariance[0] = 1000000;
            imu.orientation_covariance[1] = 0;
            imu.orientation_covariance[2] = 0;
            imu.orientation_covariance[3] = 0;
            imu.orientation_covariance[4] = 1000000;
            imu.orientation_covariance[5] = 0;
            imu.orientation_covariance[6] = 0;
            imu.orientation_covariance[7] = 0;
            imu.orientation_covariance[8] = 0.000001;

            imu.angular_velocity.x = 0.0;
            imu.angular_velocity.y = 0.0;
            imu.angular_velocity.z = (double)-1*(angleRate_z*3.14/(180*100));
            imu.linear_acceleration_covariance[0] = -1;
            imu_pub.publish(imu);

        }
    }
    return 0;
}
