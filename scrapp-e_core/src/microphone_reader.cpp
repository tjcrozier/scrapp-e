class MicrophoneReader: public rclcpp::Node
{
    // read microphone input
    //publish it for other nodes to read
    // create debug mode that feeds in usb mic input?  should be easier since it would just run on linux
    //not rocket science lol
    
};

int main(int argc, char * argv[])
{
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<MicrophoneReader>());
    rclcpp::shutdown();
    return 0;
}