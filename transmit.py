import inputs
import socket
import json

def send_inputs(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        while True:
            events = inputs.get_gamepad()
            for event in events:
                data = json.dumps({'type': event.ev_type, 'code': event.code, 'state': event.state})
                sock.sendto(data.encode('utf-8'), (host, port))

if __name__ == "__main__":
    send_inputs('DEVICE2', 62311)