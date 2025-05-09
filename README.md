# Object-Detecting-DSLR-Updated

This repository contains an updated version of the Object-Detection-DSLR project, a collaboration between damierej and Rohan. The project uses a DSLR camera, Arduino, and machine learning to detect motion, capture images, and identify faces and objects (hand, keys, phone) in the images.

## Project Overview

The system works as follows:
1. An Arduino with a push button (simulating motion detection) sends a `MOTION` message over serial when the button is pressed.
2. A Python script (`security_cam.py`) receives the message and triggers an AutoHotkey script (`trigger_camera.ahk`) to take a photo using Canon EOS Utility.
3. The photo (in `.CR3` format) is converted to JPEG, and face detection (using Haar Cascade) and object detection (using a fine-tuned MobileNetV2 model) are performed.
4. If faces or objects are detected, a popup notification is shown, and the Arduino is notified to activate an LED.

## Repository Structure

- `security_cam.py`: Main Python script for motion detection, image processing, and face/object detection.
- `trigger_camera.ahk`: AutoHotkey script to automate photo capture in Canon EOS Utility.
- `button_test.ino`: Arduino sketch to read the button state and send `MOTION`/`STOP` messages.
- `README.md`: Project documentation.

### Additional Files (Not Included but Required)
- `models/custom_mobilenet.h5`: Pre-trained MobileNetV2 model for object detection (must be trained and placed in the `models/` directory).
- `Cascade/haarcascade_frontalface_default.xml`: Haar Cascade file for face detection (download from OpenCV’s GitHub and place in the `Cascade/` directory).
- `dataset_resized/`: Directory containing training images for the model (subfolders: `hand/`, `keys/`, `phone/`).
- `Captured Images/`: Directory where Canon EOS Utility saves `.CR3` files (subfolder with the latest date).
- `captured_images/`: Directory where processed JPEG images are saved (created automatically).

## Prerequisites

1. **Hardware**:
   - Arduino (e.g., Uno) with a push button on a breadboard (connected to pin 2 with a 10kΩ pull-down resistor).
   - DSLR camera connected to the computer (e.g., Canon EOS 90D).
   - Computer running Windows with AutoHotkey v2 installed (`C:\Program Files\AutoHotkey\v2\AutoHotkey64.exe`).

2. **Software**:
   - Python 3.9 with the following libraries:
     ```
     pip install tensorflow==2.10.0 opencv-python-headless numpy pyserial rawpy imageio
     ```
   - Canon EOS Utility (or similar software) for capturing photos.
   - Arduino IDE for uploading the sketch to the Arduino.

## Setup Instructions

### 1. Arduino Setup
- **Wiring**:
  - Connect a push button to the Arduino:
    - One leg to 5V.
    - Opposite leg to pin 2.
    - 10kΩ resistor from pin 2 to GND (pull-down resistor).
- **Upload Code**:
  - Open `button_test.ino` in the Arduino IDE.
  - Upload the sketch to your Arduino.
  - Open the Serial Monitor (9600 baud) to verify `MOTION` and `STOP` messages when pressing/releasing the button.

### 2. Directory Structure
Create the following directory structure in your project folder:
```
Object-Detecting-DSLR-Updated/
├── security_cam.py
├── trigger_camera.ahk
├── button_test.ino
├── README.md
├── models/
│   └── custom_mobilenet.h5  (you need to train and place this file)
├── Cascade/
│   └── haarcascade_frontalface_default.xml  (download from OpenCV)
├── dataset_resized/
│   ├── hand/
│   ├── keys/
│   └── phone/
├── Captured Images/
│   └── <date_folder>/
│       └── *.CR3  (created by Canon EOS Utility)
└── captured_images/  (created automatically)
```

### 3. Update `trigger_camera.ahk`
- Open Canon EOS Utility.
- Use Window Spy (`C:\Program Files\AutoHotkey\v2\WindowSpy.ahk`) to find:
  - The window title (e.g., `EOS Utility 3`) and update `possibleTitles` in `trigger_camera.ahk`.
  - The window-relative coordinates of the shutter button (e.g., `310, 126`) and update `MouseMove`.
- If the click doesn’t work, try the key press or `ControlClick` methods (see comments in the script).

### 4. Train the Model
- Run `create_object_detection_model.py` (not included here, but referenced in the original repo) to train the MobileNetV2 model and save it as `models/custom_mobilenet.h5`.
- Ensure `dataset_resized/` contains images in subfolders `hand/`, `keys/`, and `phone/`.

### 5. Run the Project
- Open Canon EOS Utility and ensure it’s ready to take photos.
- Run `security_cam.py`:
  ```
  cd path/to/Object-Detecting-DSLR-Updated
  python security_cam.py
  ```
- Press the button on your breadboard to simulate motion:
  - The script should receive `MOTION`, trigger a photo, process the image, and show a popup if faces/objects are detected.

## Troubleshooting

- **Button Not Working**:
  - Check wiring (5V, pin 2, 10kΩ pull-down resistor).
  - Use a multimeter to test the button.
  - Verify Serial Monitor output in Arduino IDE.
- **Photo Not Taken**:
  - Run `trigger_camera.ahk` manually as admin.
  - Update window title and coordinates in `trigger_camera.ahk`.
  - Try key press or `ControlClick` methods.
- **Model Not Found**:
  - Ensure `custom_mobilenet.h5` exists in `models/`.
  - Re-run `create_object_detection_model.py` if needed.
- **Dependencies**:
  - Ensure all Python libraries are installed.
  - Use TensorFlow 2.10.0 to match the model.

## Contributors

- damiere
- Rohan

## License

This project is licensed under the MIT License.



https://github.com/user-attachments/assets/1f4747ba-a8bf-4d02-acc9-aaa6500cf83c


