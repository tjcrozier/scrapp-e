#include <chrono>
#include <memory>
#include <string>

#include <opencv2/videoio.hpp>
#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/image.hpp>

// cv_bridge header name differs between ROS 2 distros (.h on Humble, .hpp on Jazzy+)
#if __has_include(<cv_bridge/cv_bridge.hpp>)
#include <cv_bridge/cv_bridge.hpp>
#else
#include <cv_bridge/cv_bridge.h>
#endif

using namespace std::chrono_literals;

class WebcamPublisher : public rclcpp::Node
{
public:
  WebcamPublisher() : Node("webcam_publisher")
  {
    // Parameters
    device_id_ = declare_parameter<int>("device_id", 0);
    width_     = declare_parameter<int>("width", 640);
    height_    = declare_parameter<int>("height", 480);
    fps_       = declare_parameter<double>("fps", 30.0);
    frame_id_  = declare_parameter<std::string>("frame_id", "camera_link");
    topic_     = declare_parameter<std::string>("topic", "image_raw");

    publisher_ = create_publisher<sensor_msgs::msg::Image>(
      topic_, rclcpp::SensorDataQoS());

    if (!open_camera()) {
      throw std::runtime_error("Could not open camera device " + std::to_string(device_id_));
    }

    const auto period = std::chrono::duration<double>(1.0 / fps_);
    timer_ = create_wall_timer(
      std::chrono::duration_cast<std::chrono::nanoseconds>(period),
      std::bind(&WebcamPublisher::capture_and_publish, this));

    RCLCPP_INFO(get_logger(), "Publishing /%s from device %d at %dx%d @ %.1f fps",
      topic_.c_str(), device_id_, width_, height_, fps_);
  }

private:
  bool open_camera()
  {
    cap_.open(device_id_, cv::CAP_V4L2);
    if (!cap_.isOpened()) {
      cap_.open(device_id_);  // fall back to any backend
    }
    if (!cap_.isOpened()) {
      return false;
    }
    cap_.set(cv::CAP_PROP_FRAME_WIDTH, width_);
    cap_.set(cv::CAP_PROP_FRAME_HEIGHT, height_);
    cap_.set(cv::CAP_PROP_FPS, fps_);
    return true;
  }

  void capture_and_publish()
  {
    cv::Mat frame;
    if (!cap_.read(frame) || frame.empty()) {
      RCLCPP_WARN_THROTTLE(get_logger(), *get_clock(), 2000,
        "Failed to read frame; attempting to reopen camera");
      cap_.release();
      open_camera();
      return;
    }

    std_msgs::msg::Header header;
    header.stamp = now();
    header.frame_id = frame_id_;

    auto msg = cv_bridge::CvImage(header, "bgr8", frame).toImageMsg();
    publisher_->publish(*msg);
  }

  int device_id_, width_, height_;
  double fps_;
  std::string frame_id_, topic_;

  cv::VideoCapture cap_;
  rclcpp::Publisher<sensor_msgs::msg::Image>::SharedPtr publisher_;
  rclcpp::TimerBase::SharedPtr timer_;
};

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  try {
    rclcpp::spin(std::make_shared<WebcamPublisher>());
  } catch (const std::exception & e) {
    RCLCPP_FATAL(rclcpp::get_logger("webcam_publisher"), "%s", e.what());
  }
  rclcpp::shutdown();
  return 0;
}
