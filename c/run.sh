SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

#requires libevdev-dev to build
cd $SCRIPT_DIR
g++ -I/usr/include/libevdev-1.0/ -o gamepad_sender gamepad_sender.cpp -levdev && \
while true; do
    echo "Starting ./gamepad_sender..."
    ./gamepad_sender

    # Check the exit code
    EXIT_CODE=$?
    echo "./gamepad_sender exited with code $EXIT_CODE"

    # Optional: Add a delay before restarting to avoid rapid restarts
    sleep 1

    # # Optional: Break the loop if a specific exit code indicates the program should not restart
    # if [[ $EXIT_CODE -eq 0 ]]; then
    #     echo "Program exited successfully. Not restarting."
    #     break
    # fi
done