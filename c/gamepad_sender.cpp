#include <libevdev/libevdev.h>
#include <iostream>
#include <fcntl.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <cstring>
#include <unistd.h>
#include <netdb.h> 
#include <iomanip>

int main() {
    int fd = open("/dev/input/event5", O_RDONLY); // Replace X with the correct number
    libevdev *dev = nullptr;
    int rc = libevdev_new_from_fd(fd, &dev);
    if (rc < 0) {
        std::cerr << "Failed to init libevdev (" << libevdev_get_fd(dev) << ")\n";
        return 1;
    }
    std::cout << "Input device name: " << libevdev_get_name(dev) << std::endl;
    std::string receiver_ip = "DEVICE2";
    uint16_t port = 62311;

    struct addrinfo hints, *res;
    memset(&hints, 0, sizeof(hints));
    hints.ai_family = AF_INET;        // AF_INET to force IPv4
    hints.ai_socktype = SOCK_DGRAM;   // Datagram socket
    hints.ai_flags = AI_PASSIVE;      // Fill in my IP for me

    if (int status = getaddrinfo(receiver_ip.c_str(), nullptr, &hints, &res) != 0) {
        std::cerr << "getaddrinfo error: " << gai_strerror(status) << std::endl;
        return 1;
    }

    // Create the socket
    int sockfd = socket(res->ai_family, res->ai_socktype, res->ai_protocol);
    if (sockfd < 0) {
        std::cerr << "Error creating socket: " << strerror(errno) << std::endl;
        freeaddrinfo(res);
        return 1;
    }

    // Configure the socket address
    struct sockaddr_in* servaddr = (struct sockaddr_in *)res->ai_addr;
    servaddr->sin_port = htons(port);  // Set port

    std::cout << "Socket setup complete for " << receiver_ip << ":" << port << ". You can now use this socket to send data." << std::endl;
    
    struct sockaddr_in* ipv4 = (struct sockaddr_in *)res->ai_addr;

    // Buffer to store the converted IP address
    char ipstr[INET_ADDRSTRLEN];

    // Convert the binary IP address to a string
    inet_ntop(AF_INET, &(ipv4->sin_addr), ipstr, sizeof(ipstr));

    std::cout << "Attempting to send data to IP: " << ipstr << " on port " << ntohs(servaddr->sin_port) << std::endl;

    struct input_event ev;
    while (libevdev_next_event(dev, LIBEVDEV_READ_FLAG_NORMAL, &ev) == 0) {
        if (ev.type == EV_KEY || ev.type == EV_ABS) {
            std::ostringstream ss;
            ss << "{\"type\": " << ev.type << ", \"code\": " << ev.code << ", \"value\": " << ev.value << "}";
            std::string json_str = ss.str();
            std::cout << ss.str() << std::endl;
            ssize_t sent = sendto(sockfd,
                      json_str.c_str(),
                      json_str.size(),
                      0,
                      reinterpret_cast<struct sockaddr*>(servaddr),
                      sizeof(*servaddr));            if (sent == -1) {
                std::cerr << "WARNING - failed to send message: " << strerror(errno) << std::endl;
            } else {
                std::cout << "Successfully sent " << sent << " bytes" << std::endl;
            }
        }
    }

    close(sockfd);
    freeaddrinfo(res);
    return 0;
}
