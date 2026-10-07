#include "rclcpp/rclcpp.hpp"

class MyNode : public rclcpp::Node
{
public:
   MyNode() : Node("my_node") {
      RCLCPP_INFO(get_logger(), "Node started!");
   }
private:
};

int main(int argc, char * argv[])
{
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<MyNode>());
    rclcpp::shutdown();
    return 0;
}
    