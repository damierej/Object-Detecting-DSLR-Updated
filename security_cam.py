import serial
import subprocess
import time
import cv2
import numpy as np
import tensorflow as tf
import os
import rawpy
import imageio
from datetime import datetime
import tkinter as tk
import threading
from tensorflow import keras


# Function to show a custom popup notification in a separate thread
def show_popup(message):
    def popup():
        root = tk.Tk()
        root.title("Detection Alert")
        root.geometry("350x150+50+50")  # Size and position (width x height + x + y)
        root.configure(bg="#f0f0f0")  # Light gray background
        
        # Make the window appear on top of all other windows
        root.attributes('-topmost', True)
        root.lift()
        root.focus_force()  # Force focus on the window
        
        # Create a label with the message, using a larger font
        label = tk.Label(
            root,
            text=message,
            wraplength=320,  # Wrap text if too long
            justify="left",
            font=("Arial", 12),
            bg="#f0f0f0",
            fg="#333333"  # Dark gray text
        )
        label.pack(pady=20)

        # Auto-dismiss after 5 seconds
        root.after(5000, root.destroy)
        root.mainloop()
    
    # Run the popup in a separate thread to avoid blocking the main script
    threading.Thread(target=popup, daemon=True).start()

# Determine the absolute base directory of the script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Initialize Arduino Serial communication
arduino = serial.Serial('COM3', 9600, timeout=1)
time.sleep(2)  # Wait for Arduino to initialize

# Create a folder to save captured images using absolute path
SAVE_FOLDER = os.path.join(BASE_DIR, 'captured_images')
if not os.path.exists(SAVE_FOLDER):
    os.makedirs(SAVE_FOLDER)

# Load Haar Cascade for face detection using absolute path
CASCADE_PATH = os.path.join(BASE_DIR, 'Cascade', 'haarcascade_frontalface_default.xml')
face_cascade = cv2.CascadeClassifier(CASCADE_PATH)
if face_cascade.empty():
    print(f"Error: Could not load Haar Cascade for face detection at {CASCADE_PATH}")
    exit()

# Load the fine-tuned MobileNetV2 model using absolute path
MODEL_PATH = os.path.join(BASE_DIR, 'models', 'custom_mobilenet.h5')
model = tf.keras.models.load_model(MODEL_PATH)

# Variable to track motion state (for consecutive photos)
motion_active = False
last_photo_time = 0
photo_interval = 2  # Reduced to 2 seconds for faster consecutive shots

# Absolute path to the AutoHotkey script
AHK_SCRIPT_PATH = os.path.join(BASE_DIR, 'trigger_camera.ahk')

# Absolute path to the Security folder where CR3 files are saved
SECURITY_BASE = os.path.join(BASE_DIR, 'Captured Images')
# Dynamically find the latest date folder
date_folders = [f for f in os.listdir(SECURITY_BASE) if os.path.isdir(os.path.join(SECURITY_BASE, f))]
if date_folders:
    latest_date = max(date_folders)
    SECURITY_FOLDER = os.path.join(SECURITY_BASE, latest_date)
else:
    print("No date folders found in Captured Images!")
    exit()

while True:
    if arduino.in_waiting > 0:
        try:
            message = arduino.readline().decode('utf-8', errors='ignore').strip()
            if message:
                print(f"Received: {message}")
                if message == "MOTION":
                    motion_active = True
                    current_time = time.time()
                    if current_time - last_photo_time >= photo_interval:
                        # Trigger the AutoHotkey script to take a photo
                        try:
                            process = subprocess.run(
                                [r'C:\Program Files\AutoHotkey\v2\AutoHotkey64.exe', AHK_SCRIPT_PATH],
                                check=True,
                                capture_output=True,
                                text=True,
                                timeout=30
                            )
                            last_photo_time = current_time
                            print("Photo taken! AutoHotkey process completed. Output:", process.stdout)
                            if process.stderr:
                                print("AutoHotkey stderr:", process.stderr)
                        except subprocess.CalledProcessError as e:
                            print(f"AutoHotkey process failed: {e}")
                            print(f"Error output: {e.stderr}")
                            continue
                        except subprocess.TimeoutExpired as e:
                            print(f"AutoHotkey process timed out: {e}")
                            continue

                        time.sleep(5)  # Increased to 5 seconds to ensure CR3 file saves

                        # Find the latest CR3 file in the Security folder
                        cr3_files = [f for f in os.listdir(SECURITY_FOLDER) if f.lower().endswith('.cr3')]
                        if cr3_files:
                            latest_cr3 = max(cr3_files, key=lambda x: os.path.getmtime(os.path.join(SECURITY_FOLDER, x)))
                            cr3_path = os.path.join(SECURITY_FOLDER, latest_cr3)
                            print(f"Found CR3 file: {cr3_path}")

                            # Convert CR3 to JPEG using rawpy
                            with rawpy.imread(cr3_path) as raw:
                                rgb = raw.postprocess()
                            jpg_path = os.path.join(SAVE_FOLDER, f'temp_{datetime.now().strftime("%Y%m%d_%H%M%S")}.jpg')
                            imageio.imsave(jpg_path, rgb)
                            print(f"Converted CR3 to JPEG: {jpg_path}")

                            # Load the JPEG for processing
                            image = cv2.imread(jpg_path)
                            if image is None:
                                print(f"Failed to load converted image: {jpg_path}")
                                continue

                            # Face detection with Haar Cascade (tuned parameters)
                            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.05, minNeighbors=2, minSize=(15, 15))
                            face_detected = len(faces) > 0

                            # Object detection with fine-tuned MobileNetV2
                            image_resized = cv2.resize(image, (224, 224))
                            image_normalized = image_resized / 255.0
                            image_expanded = np.expand_dims(image_normalized, axis=0)
                            predictions = model.predict(image_expanded)
                            class_indices = {0: 'hand', 1: 'phone', 2: 'keys'}  # Update based on your training folders
                            predicted_class = class_indices[np.argmax(predictions[0])]
                            confidence = np.max(predictions[0])
                            object_detected = confidence > 0.5
                            detected_objects = [f"{predicted_class} ({confidence:.2f})"] if object_detected else []

                            # Debug output
                            print(f"Debug - Faces detected: {len(faces)}, Objects detected: {object_detected}, Predicted: {detected_objects}")

                            # If faces or objects are detected, notify Arduino and show popup
                            if face_detected or object_detected:
                                # Build a conversational popup message
                                popup_message = "I detected something!\n"
                                if face_detected:
                                    popup_message += f"I see {len(faces)} face{'s' if len(faces) > 1 else ''}!\n"
                                if object_detected:
                                    for obj in detected_objects:
                                        obj_name, obj_conf = obj.split(' (')
                                        obj_conf = obj_conf.rstrip(')')
                                        popup_message += f"This object is a {obj_name}! (I'm {float(obj_conf) * 100:.0f}% sure)\n"

                                # Show the popup notification
                                show_popup(popup_message)

                                # Print to console and notify Arduino
                                print("Detection triggered:")
                                if face_detected:
                                    print(f"  - Faces detected: {len(faces)}")
                                if object_detected:
                                    print("  - Objects detected:")
                                    for obj in detected_objects:
                                        print(f"    - {obj}")
                                arduino.write(b"DETECTED\n")  # Send command to Arduino
                                print("LED activated via Arduino!")
                            else:
                                print("No face or object detected.")

                            # Save the processed image with a timestamp
                            processed_image_path = os.path.join(SAVE_FOLDER, f'processed_{datetime.now().strftime("%Y%m%d_%H%M%S")}.jpg')
                            cv2.imwrite(processed_image_path, image)
                            print(f"Processed image saved: {processed_image_path}")
                        else:
                            print("No CR3 files found in Security folder!")
                elif message == "STOP":
                    motion_active = False
                    last_photo_time = 0  # Reset for next motion event
                    arduino.write(b"STOP\n")  # Notify Arduino to turn off LED/buzzer
        except UnicodeDecodeError:
            print("Received invalid data, skipping...")
        except Exception as e:
            print(f"Unexpected error: {e}")

# Cleanup
arduino.close()