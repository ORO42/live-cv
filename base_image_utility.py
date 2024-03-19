from stream import Stream
import cv2

stream = Stream(twitch_username="example_username")

try:
    stream.connect()
    while True:
        frame = stream.read_frame()
        key = cv2.waitKey(1) & 0xFF

        if frame is not None:
            # press enter to save screenshot
            if key == ord("\r"):
                stream.screenshot(frame=frame)
                print("Screenshot saved")

        if key == ord("q"):
            break  # Exit loop if 'q' key is pressed
finally:
    stream.disconnect()
    cv2.destroyAllWindows()
