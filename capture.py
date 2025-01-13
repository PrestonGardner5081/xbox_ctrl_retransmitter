import socket
import json
import pyvjoy

def receive_inputs(port):
    j = pyvjoy.VJoyDevice(1)  # Assumes vJoy device 1 is configured
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind(('', port))
        while True:
            data, addr = sock.recvfrom(1024)
            event = json.loads(data.decode('utf-8'))
            if event['type'] == 'Absolute':  # Example: process only Absolute events
                j.set_axis(pyvjoy.HID_USAGE_X, event['state'])  # Map events to vJoy axes/buttons

if __name__ == "__main__":
    receive_inputs(12345)  # Use the same port as in the sender script
