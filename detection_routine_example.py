from detection import Detection
from stream import Stream
import cv2
from sys import exit


def example_callback():
    print("Feature detected!")
    exit("All feature recognition stopped")


# Instantiate a Stream
stream = Stream(twitch_username="example_username")

# Instantiate a Detection
detection1 = Detection(
    "config_files/tarkov.json",
    template_id="e4e7a9ad",  # comes from the log file
    threshold=5,  # Hamming distance required to be considered a match
    stream=stream,
    callback_function=example_callback,
)

try:
    stream.connect()
    while True:
        detection1.detect()
        # You could choose to instantiate another Dectection class and start detecting with it after a detection1 callback is triggered

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break  # Exit loop if 'q' key is pressed
finally:
    stream.disconnect()
