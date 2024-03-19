from collections import deque
import json
import cv2
import imagehash
from PIL import Image


class Detection:
    def __init__(
        self,
        config_file_path: str,
        template_id: str,
        threshold: int,
        stream,
        callback_function=None,
    ):
        self.config_file_path = config_file_path
        self.template_id = template_id
        self.threshold = threshold
        self.stream = stream
        self.callback_function = callback_function
        self.template_data = self.get_data_by_template_id()
        self.template_image = cv2.imread(self.template_data["screenshot_path"])
        self.template_image_x1 = self.template_data["screenshot_pos"]["top_left"]["x1"]
        self.template_image_y1 = self.template_data["screenshot_pos"]["top_left"]["y1"]
        self.template_image_x2 = self.template_data["screenshot_pos"]["bottom_right"][
            "x2"
        ]
        self.template_image_y2 = self.template_data["screenshot_pos"]["bottom_right"][
            "y2"
        ]

        self.frame_deque = deque()

    # Retrieve template data based on template_id from the config file
    def get_data_by_template_id(self):
        try:
            with open(self.config_file_path, "r") as json_file:
                data = json.load(json_file)
                for entry in data:
                    if entry.get("template_id") == self.template_id:
                        return entry
                print(f"No entry found with template_id: {self.template_id}")
                return None
        except FileNotFoundError:
            print(f"File not found: {self.config_file_path}")
            return None
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return None

    def avg_hash(self, haystack):
        formatted_needle = Image.fromarray(self.template_image)
        formatted_haystack = Image.fromarray(haystack)
        needle_hash = imagehash.average_hash(formatted_needle)
        haystack_hash = imagehash.average_hash(formatted_haystack)
        return needle_hash - haystack_hash

    def roi_crop(self, source, y1, y2, x1, x2):
        return source[y1:y2, x1:x2]

    def detect(self):
        frame = self.stream.read_frame()
        if frame is not None:
            self.frame_deque.appendleft(frame)
            roi = self.roi_crop(
                self.frame_deque.pop(),
                self.template_image_y1,
                self.template_image_y2,
                self.template_image_x1,
                self.template_image_x2,
            )
            hamming = self.avg_hash(roi)
            if hamming < self.threshold:
                if self.callback_function:
                    self.callback_function()

                # resolve the detection instance
                # cv2.destroyAllWindows()
                return

            cv2.imshow("roi_frame", roi)
            cv2.waitKey(1)
