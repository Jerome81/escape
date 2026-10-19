import time
from gpiozero import DigitalInputDevice
from signal import pause

# Use DigitalInputDevice with pull-up resistor to see RAW, unfiltered signals
# Change 2 to your actual GPIO pin number
button_raw = DigitalInputDevice(2, pull_up=True)

# Global variables to track the timing of the bounce event
last_stable_time = 0
bounce_timestamps = []

def pin_changed():
    global last_stable_time, bounce_timestamps
    current_time = time.time() * 1000  # Convert to milliseconds
    
    # If this is the start of a new press after a period of quiet (e.g., 500ms)
    if current_time - last_stable_time > 500:
        bounce_timestamps = [current_time]
        print("\n--- New Press Detected ---")
    else:
        # Record the timestamp of this specific bounce
        bounce_timestamps.append(current_time)
    
    last_stable_time = current_time
    
    # Calculate total duration from the very first contact to this bounce
    total_bounce_duration = bounce_timestamps[-1] - bounce_timestamps[0]
    bounce_count = len(bounce_timestamps)
    
    print(f"Bounce #{bounce_count} caught! Cumulative bounce time: {total_bounce_duration:.2f} ms")

# Trigger the function on both falling and rising edges (any electrical change)
button_raw.when_activated = pin_changed
button_raw.when_deactivated = pin_changed

print("Measurement ready. Press the button firmly once...")
pause()
