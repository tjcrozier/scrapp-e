cmake_minimum_required(VERSION 3.8)
project(webcam_publisher)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(std_msgs REQUIRED)
find_package(cv_bridge REQUIRED)
find_package(OpenCV REQUIRED COMPONENTS core videoio)

add_executable(webcam_publisher src/webcam_publisher.cpp)
target_include_directories(webcam_publisher PRIVATE ${OpenCV_INCLUDE_DIRS})
target_link_libraries(webcam_publisher ${OpenCV_LIBS})
ament_target_dependencies(webcam_publisher rclcpp sensor_msgs std_msgs cv_bridge)

install(TARGETS webcam_publisher DESTINATION lib/${PROJECT_NAME})

ament_package()
