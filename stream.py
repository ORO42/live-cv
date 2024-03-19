import streamlink
import cv2
import os
import uuid
from collections import deque


class Stream:
    def __init__(
        self, twitch_username, headless=False, stream_quality="best", stream_fps=30.0
    ):
        self.twitch_username = twitch_username
        self.stream_url = f"https://www.twitch.tv/{twitch_username}"
        self.stream_quality = stream_quality
        self.stream_fps = stream_fps
        self.cap = None
        self.headless = headless

    def connect(self):
        streams = streamlink.streams(self.stream_url)
        if streams:
            self.cap = cv2.VideoCapture(streams[self.stream_quality].to_url())
            print("Stream started")
        else:
            raise ValueError("No streams were available")

    def read_frame(self):
        if self.cap:
            ret, frame = self.cap.read()
            if ret:
                if not self.headless:
                    cv2.imshow("stream_frame", frame)
                return frame
        return None

    def disconnect(self):
        if self.cap:
            self.cap.release()

    def screenshot(self, frame, folder="base_images"):
        # Create the folder if it doesn't exist
        os.makedirs(folder, exist_ok=True)

        # Construct a random ID for the saved image file name
        random_id = str(uuid.uuid4().hex)[:8]  # Use the first 8 characters
        filename = f"base_{random_id}.png"

        # Save the current frame as a screenshot
        filepath = os.path.join(folder, filename)
        cv2.imwrite(filepath, frame)
        print(f"Screenshot saved as {filepath}")
