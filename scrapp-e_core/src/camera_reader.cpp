
class CameraReader : public rclcpp::Node
{
    // ...
};


int main(int argc, char * argv[])
{
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<CameraReader>());
    rclcpp::shutdown();
    return 0;
}