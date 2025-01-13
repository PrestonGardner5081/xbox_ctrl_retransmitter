import socket
import json
import pyvjoy
import logging

# -----------------------------
# Event Type Definitions
# -----------------------------
EV_KEY = 0x01
EV_ABS = 0x03

# -----------------------------
# Xbox Button Codes (common)
# -----------------------------
BTN_A       = 304  # "South" button (A)
BTN_B       = 305  # "East"  button (B)
BTN_X       = 307  # "West"  button (X)
BTN_Y       = 308  # "North" button (Y)
BTN_TL      = 310  # Left bumper (LB)
BTN_TR      = 311  # Right bumper (RB)
BTN_THUMBL  = 317  # Left stick click
BTN_THUMBR  = 318  # Right stick click
BTN_START   = 315
BTN_SELECT  = 314

# -----------------------------
# Xbox ABS (Axis) Codes (common)
# -----------------------------
ABS_X       = 0    # Left stick X
ABS_Y       = 1    # Left stick Y
ABS_Z       = 2    # Left trigger   (sometimes)
ABS_RX      = 3    # Right stick X
ABS_RY      = 4    # Right stick Y
ABS_RZ      = 5    # Right trigger  (sometimes)
ABS_HAT0X   = 16   # D-Pad left/right
ABS_HAT0Y   = 17   # D-Pad up/down

def normalize_axis(value):
    """
    Convert a signed 16-bit value (-32768..32767)
    into an unsigned 0..32767 range for pyvjoy.
    """
    return (value + 32768) // 2

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def receive_inputs(port):
    # Create a vJoy device object (device #1 assumed)
    j = pyvjoy.VJoyDevice(1)

    logging.info(f"Listening for incoming data on port {port}")
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind(('', port))
        try:
            while True:
                # Receive up to 1024 bytes
                data, addr = sock.recvfrom(1024)
                logging.info(f"Received data from {addr}: {data}")

                # Parse JSON
                event = json.loads(data.decode('utf-8'))
                logging.debug(f"Processing event: {event}")

                evt_type = event.get('type')
                evt_code = event.get('code')
                evt_value = event.get('value')

                if evt_type == EV_KEY:
                    # Process button events
                    # Mapping: your choice how to map codes -> vJoy button numbers
                    if evt_code == BTN_A:
                        j.set_button(1, evt_value)  # A -> Button #1
                    elif evt_code == BTN_B:
                        j.set_button(2, evt_value)  # B -> Button #2
                    elif evt_code == BTN_X:
                        j.set_button(3, evt_value)  # X -> Button #3
                    elif evt_code == BTN_Y:
                        j.set_button(4, evt_value)  # Y -> Button #4
                    elif evt_code == BTN_TL:
                        j.set_button(5, evt_value)  # LB
                    elif evt_code == BTN_TR:
                        j.set_button(6, evt_value)  # RB
                    elif evt_code == BTN_START:
                        j.set_button(7, evt_value)  # START
                    elif evt_code == BTN_SELECT:
                        j.set_button(8, evt_value)  # BACK
                    elif evt_code == BTN_THUMBL:
                        j.set_button(9, evt_value)  # Left stick click
                    elif evt_code == BTN_THUMBR:
                        j.set_button(10, evt_value) # Right stick click
                    # ...add more if you like

                elif evt_type == EV_ABS:
                    # Process analog axes
                    if evt_code == ABS_X:
                        j.set_axis(pyvjoy.HID_USAGE_X, normalize_axis(evt_value))
                    elif evt_code == ABS_Y:
                        j.set_axis(pyvjoy.HID_USAGE_Y, normalize_axis(evt_value))
                    elif evt_code == ABS_RX:
                        j.set_axis(pyvjoy.HID_USAGE_RX, normalize_axis(evt_value))
                    elif evt_code == ABS_RY:
                        j.set_axis(pyvjoy.HID_USAGE_RY, normalize_axis(evt_value))
                    elif evt_code == ABS_Z:
                        # Could treat as left trigger or something else
                        j.set_axis(pyvjoy.HID_USAGE_Z, normalize_axis(evt_value))
                    elif evt_code == ABS_RZ:
                        # Could treat as right trigger
                        j.set_axis(pyvjoy.HID_USAGE_RZ, normalize_axis(evt_value))
                    elif evt_code == ABS_HAT0X:
                        # D-Pad left/right
                        logging.debug(f"DPAD X event value: {evt_value}")

                        if evt_value == -1:
                            j.set_button(11, 1)  # D-pad left
                            j.set_button(12, 0)  # Ensure right is not pressed
                        elif evt_value == 1:
                            j.set_button(12, 1)  # D-pad right
                            j.set_button(11, 0)  # Ensure left is not pressed
                        else:
                            j.set_button(11, 0)  # Release left
                            j.set_button(12, 0)  # Release right
                    elif evt_code == ABS_HAT0Y:
                        # D-Pad up/down
                        logging.debug(f"DPAD Y event value: {evt_value}")

                        if evt_value == -1:
                            j.set_button(13, 1)  # D-pad up
                            j.set_button(14, 0)  # Ensure down is not pressed
                        elif evt_value == 1:
                            j.set_button(14, 1)  # D-pad down
                            j.set_button(13, 0)  # Ensure up is not pressed
                        else:
                            j.set_button(13, 0)  # Release up
                            j.set_button(14, 0)  # Release down
        except Exception as e:
            logging.error(f"Error receiving or processing data: {str(e)}")
        finally:
            logging.info("Receiver socket closed")

if __name__ == "__main__":
    receive_inputs(62311)
