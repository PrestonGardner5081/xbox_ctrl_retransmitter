import inputs
import socket
import json
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')  # Set to DEBUG to see all logs

def send_inputs(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        logging.info(f"Starting to send inputs to {host}:{port}")
        try:
            while True:
                events = inputs.get_gamepad()
                if not events:
                    logging.debug("No input events detected.")
                for event in events:
                    data = json.dumps({'type': event.ev_type, 'code': event.code, 'state': event.state})
                    logging.debug(f"Sending: {data}")
                    sock.sendto(data.encode('utf-8'), (host, port))
        except Exception as e:
            logging.error(f"Error sending data: {str(e)}")
        finally:
            logging.info("Sender socket closed")

if __name__ == "__main__":
    send_inputs('DEVICE2', 62311)  # Change to the target IP and port
