import os
import sys
import math
import cv2
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import json
import time
from utils.detections_utils import run_detection, load_detections
from utils.clock_utils import draw_clock, get_box_center, calculate_angle, process_clock_time


class ClockDetectionApp:
    def __init__(self, master):
        self.master = master
        master.title("Clock Time Detection")
        master.geometry("1000x700")  # Increased size for better visibility

        # Style
        self.style = ttk.Style()
        self.style.configure("TButton", padding=10, font=('Arial', 10))
        self.style.configure("TLabel", font=('Arial', 10))

        # Top frame for controls
        control_frame = tk.Frame(master)
        control_frame.pack(pady=10)

        # Confidence slider
        tk.Label(control_frame, text="Confidence Threshold:").pack(side=tk.LEFT, padx=(0,10))
        self.confidence_var = tk.DoubleVar(value=0.5)
        self.confidence_slider = tk.Scale(control_frame, from_=0.1, to=1.0, resolution=0.1, 
                                           orient=tk.HORIZONTAL, length=300, 
                                           variable=self.confidence_var)
        self.confidence_slider.pack(side=tk.LEFT)

        # Button frame
        button_frame = tk.Frame(master)
        button_frame.pack(pady=10)

        # Buttons
        self.single_image_button = ttk.Button(button_frame, text="Select Single Image", command=self.process_single_image)
        self.single_image_button.pack(side=tk.LEFT, padx=10)

        self.folder_button = ttk.Button(button_frame, text="Select Folder", command=self.process_folder)
        self.folder_button.pack(side=tk.LEFT, padx=10)

        # Results frame
        results_frame = tk.Frame(master)
        results_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        # Left side for results text
        results_text_frame = tk.Frame(results_frame)
        results_text_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        
        self.results_text = tk.Text(results_text_frame, height=20, width=50, wrap=tk.WORD)
        self.results_text.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        
        results_scrollbar = tk.Scrollbar(results_text_frame, command=self.results_text.yview)
        results_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.results_text.config(yscrollcommand=results_scrollbar.set)

        # Right side for images
        image_frame = tk.Frame(results_frame)
        image_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

        # Original image label
        self.original_image_label = tk.Label(image_frame, text="Original Image")
        self.original_image_label.pack()

        # Detection image label
        self.detection_image_label = tk.Label(image_frame, text="Detection Image")
        self.detection_image_label.pack()

    def process_single_image(self):
        image_path = filedialog.askopenfilename(
            title="Select Clock Image", 
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")]
        )
        if image_path:
            self.process_image(image_path)

    def process_folder(self):
        folder_path = filedialog.askdirectory(title="Select Folder with Clock Images")
        if folder_path:
            image_files = [
                os.path.join(folder_path, f) for f in os.listdir(folder_path) 
                if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))
            ]
            
            self.results_text.delete(1.0, tk.END)
            self.original_image_label.config(image='', text="Original Image")
            self.detection_image_label.config(image='', text="Detection Image")
            
            for image_path in image_files:
                self.process_image(image_path, append_results=True)

    def process_image(self, image_path, append_results=False):
        confidence = self.confidence_var.get()
        
        try:
            # Run detection
            detections = run_detection(image_path, confidence=confidence)
            
            # Process clock time
            result = process_clock_time(detections, image_path)
            
            # Display results
            result_text = f"Image: {os.path.basename(image_path)}\n"
            if result:
                if result['seconds'] is not None:
                    result_text += f"Time: {result['hours']:02d}:{result['minutes']:02d}:{result['seconds']:02d}\n"
                else:
                    result_text += f"Time: {result['hours']:02d}:{result['minutes']:02d}\n"
            else:
                result_text += "Time detection failed\n"
            result_text += "-" * 40 + "\n"
            
            if append_results:
                self.results_text.insert(tk.END, result_text)
            else:
                self.results_text.delete(1.0, tk.END)
                self.results_text.insert(tk.END, result_text)
            
            self.results_text.see(tk.END)
            
            # Organize detections by class_name
            detections_by_class = {}
            for detection in detections[0]:
                class_name = detection['class_name']
                if class_name not in detections_by_class or detection['confidence'] > detections_by_class[class_name]['confidence']:
                    detections_by_class[class_name] = detection
            
            # Draw clock visualization
            if all(key in detections_by_class for key in ['hours', 'minutes', '12', 'circle']):
                # Calculate points
                circle_box_point = get_box_center(detections_by_class['circle']['box'])
                center_point = get_box_center(detections_by_class['center']['box']) if 'center' in detections_by_class else circle_box_point
                hours_point = get_box_center(detections_by_class['hours']['box'])
                minutes_point = get_box_center(detections_by_class['minutes']['box'])
                number_12_point = get_box_center(detections_by_class['12']['box'])
                
                # Prepare for drawing
                seconds_point = get_box_center(detections_by_class['seconds']['box']) if 'seconds' in detections_by_class else None
                
                # Calculate angles
                hour_angle = calculate_angle(center_point, hours_point, number_12_point)
                minute_angle = calculate_angle(center_point, minutes_point, number_12_point)
                seconds_angle = calculate_angle(center_point, seconds_point, number_12_point) if seconds_point else None
                
                # Draw the clock visualization
                draw_clock(
                    image_path, 
                    center_point, 
                    hours_point, 
                    minutes_point, 
                    seconds_point, 
                    number_12_point, 
                    hour_angle, 
                    minute_angle, 
                    seconds_angle, 
                    result['hours'], 
                    result['minutes'], 
                    result.get('seconds', 0),
                    f"{os.path.splitext(os.path.basename(image_path))[0]}_clock.jpg"
                )
                
                # Display the newly drawn clock image
                clock_final_path = f'results/{os.path.splitext(os.path.basename(image_path))[0]}_clock.jpg'
                if os.path.exists(clock_final_path):
                    final_pil_img = Image.open(clock_final_path)
                    final_pil_img.thumbnail((400, 400))
                    final_photo = ImageTk.PhotoImage(final_pil_img)
                    self.original_image_label.config(image=final_photo, text="")
                    self.original_image_label.image = final_photo
            
            # Display detection image (keep existing code)
            detection_path = f'examples/{os.path.splitext(os.path.basename(image_path))[0]}_detection.jpg'
            print(f"Attempting to load detection image from: {detection_path}")
            
            time.sleep(1)  # Wait for file to be written
            
            if os.path.exists(detection_path):
                print("Detection image found!")
                detection_pil_img = Image.open(detection_path)
                detection_pil_img.thumbnail((400, 400))
                detection_photo = ImageTk.PhotoImage(detection_pil_img)
                self.detection_image_label.config(image=detection_photo, text="")
                self.detection_image_label.image = detection_photo
            else:
                print(f"Detection image not found at {detection_path}")
                self.detection_image_label.config(image='', text="No Detection Image")
            
        except Exception as e:
            print(f"Error processing image: {e}")
            messagebox.showerror("Error", f"An error occurred: {e}")



def main():
    root = tk.Tk()
    app = ClockDetectionApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()