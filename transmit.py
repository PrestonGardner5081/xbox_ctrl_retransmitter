import inputs

def print_inputs():
    while True:
        events = inputs.get_gamepad()
        for event in events:
            print(f"Event Type: {event.ev_type}, Code: {event.code}, State: {event.state}")

if __name__ == "__main__":
    print_inputs()