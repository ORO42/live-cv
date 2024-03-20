# Usage

1. In `base_image_utility.py`, provide the URL of an active Twitch steam to the `stream` instance
   - This opens the Twitch stream in a window (you may see default Twitch messages for some time before the stream becomes visible. These messages may also happen when ads play on the stream)
2. When a desired trigger appears in the stream window, press the "enter" key to capture a screenshot to be used as a base image
   - The screenshot size is equal to the size of the inbound stream frame it was taken from
   - Screenshots are saved in the `base_images` directory
   - You can press enter as many times as you'd like to capture screenshots without having to restart the steam
3. Press "q" to quit the utility once you are finished collecting your base images
4. Run `template_utility.py`
5. Select one of your base images from the `base_images` directory when prompted
6. Click two points on the image to draw a bounding rectangle around the feature you want to detect
   - You can backspace to undo one point at a time, starting with the last placed point, which helps with fine tuning your selection
   - You can have a maximum of one bounding rectangle per run of the utility
7. Press "enter" when you're ready to finalize your selection
8. Select whether or not you would like to add the data for your new selection to an existing config file, or create a new config file.
   - If you elected to create a new config file, be sure it's in the "config_files" directory
   - Once completed, an image cropped to the size of your selection will be saved to the `template_images` directory, and the config data will be saved to the location you chose.
9. Exit window
10. Create a .py file where you will build the logic for your detection routine (e.g. `detection_routine_1.py`)
11. See `detection_routine_example.py` for an example on how you can set up your logic
12. You can press 'q' to exit the detection process.

- The inbound stream coming from streamlink may be slowed or choppy
- When closing a window through a keyboard event, you may need to press the key multiple times

# ✏️ Project writeup

### 🫢 Oops

I originally coded this system towards the end of 2019 while home from college due to covid on an old gaming laptop that suddenly and inexplicably bit the dust. Apparently, some major data corruption occured and I lost everything on the machine. I swear I hadn't visited any untrustworthy sites 👀! In all seriousness, I had had problems with it in the past with blue-screens, and refusal to power up. I finished this project, got busy with school, and got another laptop. When I had the thought to go back and check out some of my old projects and upload them to GitHub, my heart sank when it wouldn't do... anything... lesson learned. I didn't have the bandwidth or a reason to re-implement at that time. So, in 2024 I finally re-implemented a subset of the components from the original system that I feel demonstrate my development and problem solving skills 😁.

### Summary

This project consists of several components from a project I built that scrapes visual data from Twitch streams in real time using computer vision techniques. I am using difference hashing to efficiently check for the presence of target visual features on the screen. With the ability to check for the presence of visual elements, we can then build further conditional logic, handling positive and negative detection cases.

The components I included in this project are the visual feature recognition mechanism, real time base-image collection utility, and template definition utility. I did not re-write the optical character recognition (OCR) processing and logging component. I will explain each of these.

My use case was performing OCR on certain text elements that appeared in a consistent region of the screen, but which may only be on the screen at certain times. Anytime other than when the target text was on the screen, other non-pertinent text could have appeared in the same region, thus breaking the system. Additionally, OCR can be a heavier process, and it would have been inefficient to perform the OCR step every processing cycle especially at times I knew the target text would not be present.

I could have just saved all the incoming stream frames and perfomed all my processing later, but I didn't want to store lots of video. I also looked into using the Twitch API to pull saved VODs from channels, but I would still need to pull in the entire video for processing, as there was no ability to "stream" a saved VOD as if it were live.

So, I opted for an in-memory "associated-trigger" approach, where I identified unique static elements that always appear on the screen at the same time as the target text, their position within the frame, and the position of the static target text in the frame. This lent a couple of key optimizations. 1. I could leverage difference hashing to very efficiently (near real time) match a hash of the template image against a hash of the region of the stream frame where I knew the target trigger would appear. 2. I didn't need to perform the more computationally intensive operation of determining _if_ text was present because I would know by default the target text region indeed contained my target text if the associated trigger or triggers were present.

I appended incoming stream frames to the rear of a fixed-length deque, calculated the Hamming distance between the trigger template image and the corresponding region of the stream frame, and popped off the front frame every processing cycle that the deque was full. I now didn't have to worry about storing VODs or memory overflow due to a huge buffer when processing multiple hour long streams. 2. Anytime a trigger event occured, I crop the triggering frame to only include the region containing the target text, then split that smaller frame off into another multiprocessing process that handles the OCR and saves the computed text into a log with the name of the trigger recognition routine and datetime of the trigger. This is the approach I used, since for each of my trigger recognition routines, there were only a few target text elements and triggers. If I was having to continuosly perform the OCR across many triggers and text targets simultaneously, I would concurrently write the target-containing image snippets, along with aforementioned identifying metadata, to a disk-based store then perform the OCR and other data science analysis once the trigger recognition routine ended.

### Improvements

I have had limited time to work on this project both times, so stopped at the in-memory trigger recognition and in-memory OCR components the first time, and just the trigger recognition part the second time. I have no plans on expanding the project further, but a feature I would have liked to add is the ability to invoke detection for other templates programatically based on key values in the JSON configs. I would accomplish this by adding a `next_template` key to each template object, which would point to the `template_id` of another template. When `template_a` resolved, `template_b` would automatically be invoked by the `Detection.detect()` method.

```json
[
  {
    "template_id": "e4e7a9ad",
    "original_image_size": {
      "width": 1792,
      "height": 1008
    },
    "screenshot_size": {
      "width": 426,
      "height": 43
    },
    "screenshot_pos": {
      "top_left": {
        "x1": 680,
        "y1": 579
      },
      "bottom_right": {
        "x2": 1106,
        "y2": 622
      }
    },
    "screenshot_path": "/path/to/template/image.png",
    "next_template": "f5e7b5lc" // optional
  }
]
```

Instead, I created a .py file for each routine, imported the Stream and Detection classes, and instantiated a Detection class for each condition I wanted to check. The `Detection.detect()` method can optionally accept a callback, which I used to establish conditionality between multiple Detection instances by chaining multiple callbacks and managing state with file-scoped variables. This was sufficient for my use cases.
