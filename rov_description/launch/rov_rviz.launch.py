import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.substitutions import LaunchConfiguration
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, ExecuteProcess
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

import xacro


def generate_launch_description():

    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')
    rov_description_dir = get_package_share_directory('rov_description')

    # Check if we're told to use sim time
    use_sim_time = LaunchConfiguration('use_sim_time')

    # Process the URDF file
    pkg_path = os.path.join(get_package_share_directory('rov_description'))
    xacro_file = os.path.join(pkg_path,'urdf','loco.urdf.xacro')
    robot_description_config = xacro.process_file(xacro_file)
    robot_description = {'robot_description': robot_description_config.toxml()}
    world_file = os.path.join(rov_description_dir, 'worlds', 'sand.world')

    # Config time simulation
    config_time = DeclareLaunchArgument(
        'use_sim_time',
        default_value='false',
        description='Use sim time if true'
    )
    
    # Create a joint_state_publisher node
    node_joint_state_publisher = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        output='screen'
    )
    
    # Create a robot_state_publisher node
    params = {'robot_description': robot_description_config.toxml(), 'use_sim_time': use_sim_time}
    node_robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[params]
    )

    # Gazebo Sim
    # gazebo = IncludeLaunchDescription(
    #     PythonLaunchDescriptionSource(
    #         os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')
    #     ),
    #     launch_arguments={'gz_args': '-r empty.sdf'}.items(),
    # )

    # RViz
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', os.path.join(pkg_path, 'rviz', 'urdf.rviz')],
    )

    # Spawn
    # spawn = Node(
    #     package='ros_gz_sim',
    #     executable='create',
    #     arguments=[
    #         '-name', 'rov_ramel',
    #         '-topic', 'robot_description',
    #     ],
    #     output='screen',
    # )

    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')),
        launch_arguments={
            'gz_args': '-r ~/ros2_ws/src/rov_robot/rov_description/worlds/sand.world'
        }.items(),
    )

    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=['/rov/th_1/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist',
                   '/rov/th_1/odometry@nav_msgs/msg/Odometry@gz.msgs.Odometry',
                   '/rov/th_2/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist',
                   '/rov/th_2/odometry@nav_msgs/msg/Odometry@gz.msgs.Odometry',
                   '/rov/th_3/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist',
                   '/rov/th_3/odometry@nav_msgs/msg/Odometry@gz.msgs.Odometry',
                   '/rov/th_4/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist',
                   '/rov/th_4/odometry@nav_msgs/msg/Odometry@gz.msgs.Odometry',
                   '/rov/th_5/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist',
                   '/rov/th_5/odometry@nav_msgs/msg/Odometry@gz.msgs.Odometry',
                   '/rov/th_6/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist',
                   '/rov/th_6/odometry@nav_msgs/msg/Odometry@gz.msgs.Odometry',],
        parameters=[{'qos_overrides./rov/th_1.subscriber.reliability': 'reliable',
                     'qos_overrides./rov/th_2.subscriber.reliability': 'reliable',
                     'qos_overrides./rov/th_3.subscriber.reliability': 'reliable',
                     'qos_overrides./rov/th_4.subscriber.reliability': 'reliable',
                     'qos_overrides./rov/th_5.subscriber.reliability': 'reliable',
                     'qos_overrides./rov/th_6.subscriber.reliability': 'reliable'}],
        output='screen'
    )

    # Launch!
    return LaunchDescription([
        config_time,
        node_robot_state_publisher,
        node_joint_state_publisher,
        # gazebo,
        rviz,
        # spawn,
        # ExecuteProcess(
        #     cmd=['gz', 'sim', '-v', '3', '-r', world_file],
        #     output='screen'
        # ),
        gz_sim,
        bridge

    ])