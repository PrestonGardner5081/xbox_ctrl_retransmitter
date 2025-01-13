import socket
import json
import logging
from pyvjoystick import vigem as vg

# -----------------------------
# Event Type Definitions
# -----------------------------
EV_KEY = 0x01
EV_ABS = 0x03

# -----------------------------
# Xbox Button Codes (common)
# -----------------------------
BTN_A = 304
BTN_B = 305
BTN_X = 307
BTN_Y = 308
BTN_TL = 310
BTN_TR = 311
BTN_THUMBL = 317
BTN_THUMBR = 318
BTN_START = 315
BTN_SELECT = 314

# -----------------------------
# Xbox ABS (Axis) Codes (common)
# -----------------------------
ABS_X = 0
ABS_Y = 1
ABS_Z = 2
ABS_RX = 3
ABS_RY = 4
ABS_RZ = 5
ABS_HAT0X = 16
ABS_HAT0Y = 17

# Xbox Button Mapping
button_map = {
    304: vg.XUSB_BUTTON.XUSB_GAMEPAD_A,
    305: vg.XUSB_BUTTON.XUSB_GAMEPAD_B,
    307: vg.XUSB_BUTTON.XUSB_GAMEPAD_X,
    308: vg.XUSB_BUTTON.XUSB_GAMEPAD_Y,
    310: vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER,
    311: vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER,
    317: vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_THUMB,
    318: vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_THUMB,
    315: vg.XUSB_BUTTON.XUSB_GAMEPAD_START,
    314: vg.XUSB_BUTTON.XUSB_GAMEPAD_BACK
}

# Initialize the VX360Gamepad
gamepad = vg.VX360Gamepad()

# Initialize joystick state
left_joystick_state = {'x': 0.0, 'y': 0.0}
right_joystick_state = {'x': 0.0, 'y': 0.0}

def normalize_trigger(value):
    """Normalize a trigger value (0..1023) to 0..255."""
    return int((value / 1023) * 255)

def normalize_axis(value):
    """Normalize a signed 16-bit value (-32768..32767) to -1.0..1.0."""
    return max(-1.0, min(1.0, value / 32767.0))
    # print(value)
    # return value

def update_left_joystick(gamepad, x_value=None, y_value=None):
    """Update the left joystick while preserving its state."""
    if x_value is not None:
        left_joystick_state['x'] = normalize_axis(x_value)
    if y_value is not None:
        left_joystick_state['y'] = normalize_axis(y_value)
    gamepad.left_joystick_float(
        x_value_float=left_joystick_state['x'],
        y_value_float=left_joystick_state['y']
    )

def update_right_joystick(gamepad, x_value=None, y_value=None):
    """Update the right joystick while preserving its state."""
    if x_value is not None:
        right_joystick_state['x'] = normalize_axis(x_value)
    if y_value is not None:
        right_joystick_state['y'] = normalize_axis(y_value)
    gamepad.right_joystick_float(
        x_value_float=right_joystick_state['x'],
        y_value_float=right_joystick_state['y']
    )

def receive_inputs(port):
    logging.info(f"Listening for incoming data on port {port}")
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind(('', port))
        try:
            while True:
                data, addr = sock.recvfrom(1024)
                logging.info(f"Received data from {addr}: {data}")
                event = json.loads(data.decode('utf-8'))
                logging.debug(f"Processing event: {event}")

                evt_type = event.get('type')
                evt_code = event.get('code')
                evt_value = event.get('value')

                if evt_type == EV_KEY:
                    button = button_map.get(evt_code)
                    if button:
                        if evt_value:  # Press button
                            gamepad.press_button(button)
                        else:  # Release button
                            gamepad.release_button(button)

                elif evt_type == EV_ABS:
                    if evt_code in [ABS_X, ABS_Y, ABS_RX, ABS_RY, ABS_Z, ABS_RZ]:
                        # Normalize joystick values
                        # value_float = evt_value / 32767.0
                        if evt_code == 0:  # ABS_X
                            update_left_joystick(gamepad, x_value=evt_value)
                        elif evt_code == 1:  # ABS_Y
                            update_left_joystick(gamepad, y_value=-evt_value)
                        elif evt_code == 3:  # ABS_RX
                            update_right_joystick(gamepad, x_value=evt_value)
                        elif evt_code == 4:  # ABS_RY
                            update_right_joystick(gamepad, y_value=-evt_value)
                        elif evt_code == 2:  # Left Trigger
                            gamepad.left_trigger(normalize_trigger(evt_value))
                        elif evt_code == 5:  # Right Trigger
                            gamepad.right_trigger(normalize_trigger(evt_value))
                    elif evt_code == ABS_HAT0X:
                        if evt_value == -1:  # D-pad left
                            gamepad.press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT)
                            gamepad.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT)
                        elif evt_value == 1:  # D-pad right
                            gamepad.press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT)
                            gamepad.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT)
                        else:  # Neutral horizontal
                            gamepad.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT)
                            gamepad.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT)

                    elif evt_code == ABS_HAT0Y:
                        if evt_value == -1:  # D-pad up
                            gamepad.press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP)
                            gamepad.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN)
                        elif evt_value == 1:  # D-pad down
                            gamepad.press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN)
                            gamepad.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP)
                        else:  # Neutral vertical
                            gamepad.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP)
                            gamepad.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN)
                # Always send the updated state to the system
                gamepad.update()

        except Exception as e:
            logging.error(f"Error receiving or processing data: {str(e)}")
        finally:
            logging.info("Receiver socket closed")

if __name__ == "__main__":
    receive_inputs(62311)