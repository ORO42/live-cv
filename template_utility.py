import json
import os
from tkinter import Tk, Canvas, Button, filedialog, messagebox
import uuid
from PIL import Image, ImageTk


class ImageSelector:
    def __init__(self, master, image_path):
        self.master = master
        self.master.title("Image Selector")

        # Load the image
        self.original_image = Image.open(image_path)
        self.image = ImageTk.PhotoImage(self.original_image)

        # Initialize variables for storing selected points
        self.points = []

        # Create Canvas to display the image
        self.canvas = Canvas(
            master, width=self.original_image.width, height=self.original_image.height
        )
        self.canvas.pack()
        self.canvas.create_image(0, 0, anchor="nw", image=self.image)

        # Bind the Enter key event to capture_screenshot
        self.master.bind("<Return>", lambda event: self.capture_screenshot())

        # Bind the click event to the canvas
        self.canvas.bind("<Button-1>", self.on_canvas_click)

        # Bind the Backspace key event to remove_last_point
        self.master.bind("<BackSpace>", lambda event: self.remove_last_point())

    def on_canvas_click(self, event):
        # Capture the coordinates of the click
        x, y = event.x, event.y

        if len(self.points) < 2:
            self.points.append((x, y))

            # Draw a point on the canvas
            self.canvas.create_oval(
                x - 5, y - 5, x + 5, y + 5, fill="red", tags="points"
            )

        # Draw a bounding box if two points are selected
        if len(self.points) == 2:
            x1, y1 = self.points[0]
            x2, y2 = self.points[1]
            self.canvas.create_rectangle(
                x1, y1, x2, y2, outline="blue", width=2, tags="rects"
            )

    def remove_last_point(self):
        x, y = self.points.pop()
        print(self.points)
        self.canvas.delete("points", "rects")
        # Redraw remaining points
        for px, py in self.points:
            self.canvas.create_oval(
                px - 5, py - 5, px + 5, py + 5, fill="red", tags="points"
            )

    def capture_screenshot(self):
        # Check if two points are selected
        if len(self.points) != 2:
            print("Please select two points.")
            return

        # Sort points to get top-left and bottom-right coordinates
        self.points.sort()

        # Get the selected area coordinates
        x1, y1 = self.points[0]
        x2, y2 = self.points[-1]

        # Crop the selected area
        selected_area = self.original_image.crop((x1, y1, x2, y2))

        # Construct the save path in 'template_images' subdirectory
        parent_directory = os.path.dirname(os.path.abspath(__file__))
        template_images_directory = os.path.join(parent_directory, "template_images")

        # Create 'template_images' directory if it doesn't exist
        os.makedirs(template_images_directory, exist_ok=True)

        # Construct a random ID for the saved image file name
        random_id = str(uuid.uuid4().hex)[:8]  # Use the first 8 characters

        # Construct the full path to the captured screenshot
        save_path = os.path.join(template_images_directory, f"template_{random_id}.png")

        # Save the cropped image
        selected_area.save(save_path)

        # Log information to a JSON file
        log_data = {
            "template_id": random_id,
            "original_image_size": {
                "width": self.original_image.width,
                "height": self.original_image.height,
            },
            "screenshot_size": {
                "width": selected_area.width,
                "height": selected_area.height,
            },
            "screenshot_pos": {
                "top_left": {"x1": x1, "y1": y1},
                "bottom_right": {"x2": x2, "y2": y2},
            },
            "screenshot_path": save_path,
        }

        # Create 'config_files' directory if it doesn't exist
        config_files_directory = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "config_files"
        )
        os.makedirs(config_files_directory, exist_ok=True)

        # Ask the user whether to select an existing JSON file or create a new one
        user_choice = messagebox.askyesno(
            "Select JSON File",
            "Do you want to select an existing JSON file?",
        )

        if user_choice:
            # Ask the user to select an existing JSON file
            json_file_name = filedialog.askopenfilename(
                filetypes=[("JSON files", "*.json")],
            )

            if json_file_name:
                # Load existing log entries from the selected JSON file
                with open(json_file_name, "r") as json_file:
                    log_entries = json.load(json_file)

                # Append the new log data
                log_entries.append(log_data)

                # Save the updated log entries back to the file
                with open(json_file_name, "w") as json_file:
                    json.dump(log_entries, json_file, indent=2)

                print(f"Config data added to existing JSON file: {json_file_name}")
        else:
            # Ask the user to specify the name of the new JSON file
            json_file_name = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json")],
                initialdir=config_files_directory,  # Set initial directory to 'config_files'
            )

            if json_file_name:
                # Create a new JSON file with the log data
                with open(json_file_name, "w") as json_file:
                    json.dump([log_data], json_file, indent=2)

                print(f"Log config saved to new JSON file: {json_file_name}")


if __name__ == "__main__":
    root = Tk()

    # Ask the user to choose an image file
    image_path = filedialog.askopenfilename(
        filetypes=[("Image files", "*.png *.jpeg *.jpg")]
    )

    if image_path:
        app = ImageSelector(root, image_path)
        root.mainloop()
    else:
        print("No image selected.")
