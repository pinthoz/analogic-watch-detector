import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import csv
import re
from utils.detections_utils import run_detection
from utils.clock_utils import draw_clock, get_box_center, calculate_angle, process_clock_with_fallback, process_clock_time
from ttkthemes import ThemedTk

class ClockDetectionApp:
    def __init__(self, master):
        self.master = master
        master.title("AnalogTimeDetector")
        master.geometry("1100x800") 
        master.resizable(False, False)
        
        icon = Image.open('img/icon.png').resize((128, 128), Image.LANCZOS)
        photo_icon = ImageTk.PhotoImage(icon)
        master.iconphoto(True, photo_icon)

        # Apply a theme for a modern look
        self.style = ttk.Style()
        self.style.theme_use('alt')

        # Header
        header_frame = ttk.LabelFrame(master, text="Settings", padding=10)
        header_frame.pack(fill=tk.X, padx=10, pady=(10, 0))

        # Confidence Threshold
        self.confidence_var = tk.DoubleVar(value=0.01)

        # CSV Output Filename
        ttk.Label(header_frame, text="Output CSV Name:").grid(row=1, column=0, sticky="w", padx=(0, 10), pady=(10, 0))
        self.csv_filename_var = tk.StringVar(value="predicted_times.csv")
        self.csv_filename_entry = ttk.Entry(header_frame, textvariable=self.csv_filename_var, width=30)
        self.csv_filename_entry.grid(row=1, column=1, sticky="w", pady=(10, 0))
        
        # Ground Truth CSV Selection Button
        self.ground_truth_path_var = tk.StringVar(value="ground_truths.csv")
        ttk.Label(header_frame, text="Ground Truth CSV:").grid(row=1, column=2, sticky="w", padx=(10, 0), pady=(10, 0))
        self.ground_truth_path_entry = ttk.Entry(header_frame, textvariable=self.ground_truth_path_var, width=30)
        self.ground_truth_path_entry.grid(row=1, column=3, sticky="w", pady=(10, 0))
        
        # Button to select ground truth CSV
        self.ground_truth_select_button = ttk.Button(header_frame, text="Browse", command=self.select_ground_truth_csv)
        self.ground_truth_select_button.grid(row=1, column=4, sticky="w", padx=(5, 0), pady=(10, 0))


        # Button section
        button_frame = ttk.LabelFrame(master, text="Actions", padding=10)
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        self.single_image_button = ttk.Button(button_frame, text="Select Single Image", command=self.process_single_image)
        self.single_image_button.grid(row=0, column=0, padx=10, pady=5, sticky="e")
        self.folder_button = ttk.Button(button_frame, text="Select Folder", command=self.process_folder)
        self.folder_button.grid(row=0, column=1, padx=10, pady=5, sticky="w")

        # Center the buttons using columnspan and rowspan
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1) 
        button_frame.grid_rowconfigure(0, weight=1)  

        # Results section
        results_frame = tk.Frame(master, borderwidth=2, relief=tk.GROOVE)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left side: Results text
        text_frame = ttk.LabelFrame(results_frame, text="Detection Results", padding=10)
        text_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=10, pady=10)

        self.results_text = tk.Text(text_frame, height=20, width=50, wrap=tk.WORD)
        self.results_text.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        results_scrollbar = tk.Scrollbar(text_frame, command=self.results_text.yview)
        results_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.results_text.config(yscrollcommand=results_scrollbar.set)

        image_frame = ttk.LabelFrame(results_frame, text="Images", padding=10)
        image_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH, padx=10, pady=10)

        self.original_image_label = ttk.Label(image_frame, text="Final Image", relief=tk.SUNKEN)
        self.original_image_label.pack(pady=5)
        self.detection_image_label = ttk.Label(image_frame, text="Detection Image", relief=tk.SUNKEN)
        self.detection_image_label.pack(pady=5)

        # Navigation buttons
        nav_frame = tk.Frame(image_frame)
        nav_frame.pack(pady=10)

        self.prev_button = ttk.Button(nav_frame, text="Previous", command=self.show_previous_image, state=tk.DISABLED)
        self.prev_button.pack(side=tk.LEFT, padx=5)
        self.next_button = ttk.Button(nav_frame, text="Next", command=self.show_next_image, state=tk.DISABLED)
        self.next_button.pack(side=tk.LEFT, padx=5)

        # Storage for predictions and image paths
        self.predictions = []
        self.image_paths = []
        self.current_index = 0
        self.ground_truth_path = "ground_truths/ground_truths_test.csv"
        self.loaded_predictions = {}


    def process_single_image(self):
        image_path = filedialog.askopenfilename(
            title="Select Clock Image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")]
        )
        if image_path:
            self.image_paths = [image_path]  # Single image
            self.current_index = 0
            self.process_image(image_path)
            self.update_navigation_buttons()
            self.save_predictions()
            
            self.predictions = []

    def process_folder(self):
        folder_path = filedialog.askdirectory(title="Select Folder with Clock Images")
        if folder_path:
            # Natural sorting of image files to handle numeric order correctly
            def natural_sort_key(filename):
                # Extract numeric parts from the filename
                return [int(text) if text.isdigit() else text.lower() 
                        for text in re.split(r'(\d+)', filename)]

            # Gather all image files in the folder and sort them using natural sorting
            self.image_paths = sorted([
                os.path.join(folder_path, f) for f in os.listdir(folder_path)
                if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))
            ], key=lambda x: natural_sort_key(os.path.basename(x)))

            if not self.image_paths:
                messagebox.showinfo("No Images", "No valid images found in the selected folder.")
                return

            self.predictions = []  # Clear predictions for a new batch
            self.results_text.delete(1.0, tk.END)

            # Process each image and store predictions
            for image_path in self.image_paths:
                self.process_image(image_path, append_results=True)

            # Save all predictions after processing
            self.save_predictions()
            self.load_predictions() 

            # Set up scrolling functionality
            self.current_index = 0
            self.update_image_display()
            self.update_navigation_buttons()

            self.predictions = []

    def update_image_display(self):
        if not self.image_paths:
            return

        image_path = self.image_paths[self.current_index]
        image_name = os.path.splitext(os.path.basename(image_path))[0]

        result_text = f"Image: {os.path.basename(image_path)}\n"

        if image_name in self.loaded_predictions:
            predicted_time = self.loaded_predictions[image_name]
            
            # Find ground truth
            ground_truth = self.find_ground_truth(image_name)
            
            if predicted_time != "failed":
                result_text += f"Predicted Time: {predicted_time}\n"
                
                # Calculate and display deviation
                if ground_truth:
                    deviation = self.calculate_time_deviation(predicted_time, ground_truth)
                    result_text += f"Ground Truth: {ground_truth}\n"
                    if deviation is not None:
                        result_text += f"Time Deviation: {deviation} seconds\n"
                    else:
                        result_text += "Time Deviation: Unable to calculate\n"
                else:
                    result_text += "Ground Truth: Not found\n"
            else:
                result_text += "Time detection failed\n"
        else:
            result_text += "Prediction not found in CSV.\n"

        result_text += "-" * 40 + "\n"

        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, result_text)
        self.results_text.see(tk.END)
        
        # Display images without processing new detections
        self.display_image(image_path)


    def process_image(self, image_path, append_results=False):
        confidence = self.confidence_var.get()

        try:
            zoom = False
            # Use the new fallback detection method
            detections = run_detection(image_path, confidence=confidence)

            result = process_clock_time(detections, image_path)
            
            if result is None:
                detections, result = process_clock_with_fallback(image_path, confidence)
                print("Fallback detection method succeeded.") if result else print("Fallback detection method failed.")
                zoom = True
                
            # Display results
            
            image_name = os.path.splitext(os.path.basename(image_path))[0]
            result_text = f"Image: {os.path.basename(image_path)}\n"

            if result:
                if result['seconds'] is not None:
                    time_str = f"{result['hours']:02d}:{result['minutes']:02d}:{result['seconds']:02d}"
                    self.predictions.append((image_name, time_str))
                if result['hours'] is not None and result['minutes'] is None:
                    time_str = f"{result['hours']:02d}:00:00"
                    self.predictions.append((image_name, time_str))
                else:
                    time_str = f"{result['hours']:02d}:{result['minutes']:02d}:00"
                    self.predictions.append((image_name, time_str))
                
                # Find and calculate ground truth deviation
                ground_truth = self.find_ground_truth(image_name)
                deviation = self.calculate_time_deviation(time_str, ground_truth)
                
                # Add time and deviation to result text
                result_text += f"Predicted Time: {time_str}\n"
                if ground_truth:
                    result_text += f"Ground Truth: {ground_truth}\n"
                    if deviation is not None:
                        result_text += f"Time Deviation: {deviation} seconds\n"
                    else:
                        result_text += "Time Deviation: Unable to calculate\n"
                else:
                    result_text += "Ground Truth: Not found\n"
            else:
                # If detection fails completely
                time_str = "failed"
                self.predictions.append((image_name, time_str))
                result_text += "Time detection failed\n"
            
            result_text += "-" * 40 + "\n"

            if append_results:
                self.results_text.insert(tk.END, result_text)
            else:
                self.results_text.delete(1.0, tk.END)
                self.results_text.insert(tk.END, result_text)

            self.results_text.see(tk.END)

            # Display the original image in the final image section
            try:
                original_pil_img = Image.open(image_path)
                original_pil_img = original_pil_img.resize((215, 215), Image.LANCZOS)
                original_photo = ImageTk.PhotoImage(original_pil_img)
                self.original_image_label.config(image=original_photo, text="")
                self.original_image_label.image = original_photo
            except Exception as e:
                print(f"Error displaying original image: {e}")
                self.original_image_label.config(image='', text="Failed to load original image")

            # Display the detection image, if it exists
            if zoom:
                # Regex para capturar 'watch_test' seguido de números
                match = re.search(r'(watch_test\d+)', image_path)
                if match:
                    extracted_id = match.group(1)
                detection_path = f'results/image_detections/{extracted_id}_zoomed_detection.jpg'
            else:
                detection_path = f'results/image_detections/{os.path.splitext(os.path.basename(image_path))[0]}_detection.jpg'
                
            if os.path.exists(detection_path):
                try:
                    detection_pil_img = Image.open(detection_path)
                    detection_pil_img = detection_pil_img.resize((215, 215), Image.LANCZOS)
                    detection_photo = ImageTk.PhotoImage(detection_pil_img)
                    self.detection_image_label.config(image=detection_photo, text="")
                    self.detection_image_label.image = detection_photo
                except Exception as e:
                    print(f"Error displaying detection image: {e}")
                    self.detection_image_label.config(image='', text="Failed to load detection image")
            else:
                self.detection_image_label.config(image='', text="No Detection Image")

            # Draw clock visualization if detections exist
            try:
                detections_by_class = {}
                for detection in detections[0]:
                    class_name = detection['class_name']
                    if class_name not in detections_by_class or detection['confidence'] > detections_by_class[class_name]['confidence']:
                        detections_by_class[class_name] = detection

                if all(key in detections_by_class for key in ['hours', '12', 'circle']):
                    # Calculate points
                    circle_box_point = get_box_center(detections_by_class['circle']['box'])
                    center_point = get_box_center(detections_by_class['center']['box']) if 'center' in detections_by_class else circle_box_point
                    hours_point = get_box_center(detections_by_class['hours']['box'])
                    number_12_point = get_box_center(detections_by_class['12']['box'])

                    # Prepare for drawing
                    seconds_point = get_box_center(detections_by_class['seconds']['box']) if 'seconds' in detections_by_class else None
                    minutes_point = get_box_center(detections_by_class['minutes']['box']) if 'minutes' in detections_by_class else None

                    # Calculate angles
                    hour_angle = calculate_angle(center_point, hours_point, number_12_point)
                    minute_angle = calculate_angle(center_point, minutes_point, number_12_point) if minutes_point else None
                    seconds_angle = calculate_angle(center_point, seconds_point, number_12_point) if seconds_point else None
                    # Draw the clock visualization
                    if zoom:
                        p = f"{os.path.splitext(os.path.basename(image_path))[0]}_clock_zoomed.jpg"
                    else:
                        p = f"{os.path.splitext(os.path.basename(image_path))[0]}_clock.jpg"
                    if zoom:
                        image_path = f'results/zoomed_images/{os.path.splitext(os.path.basename(image_path))[0]}_zoomed.jpg'
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
                        result.get('minutes', 0),
                        result.get('seconds', 0),
                        p
                    )
                    

                    # Display the newly drawn clock image
                    if zoom:
                        # Regex para capturar 'watch_test' seguido de números
                        match = re.search(r'(watch_test\d+)', image_path)
                        if match:
                            extracted_id = match.group(1)
                        clock_final_path = f'results/images/{extracted_id}_clock_zoomed.jpg'
                    else:
                        clock_final_path = f'results/images/{os.path.splitext(os.path.basename(image_path))[0]}_clock.jpg'
                    if os.path.exists(clock_final_path):
                        final_pil_img = Image.open(clock_final_path)
                        final_pil_img = final_pil_img.resize((215, 215), Image.LANCZOS)
                        final_photo = ImageTk.PhotoImage(final_pil_img)
                        self.original_image_label.config(image=final_photo, text="")
                        self.original_image_label.image = final_photo
                else:
                    print("Missing detections required to draw clock.")
            except Exception as e:
                print(f"Error drawing clock: {e}")
        except Exception as e:
            print(f"Error processing image: {e}")
            messagebox.showerror("Error", f"An error occurred: {e}")


    def show_previous_image(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.update_image_display()
            self.update_navigation_buttons()

    def show_next_image(self):
        if self.current_index < len(self.image_paths) - 1:
            self.current_index += 1
            self.update_image_display()
            self.update_navigation_buttons()


    def update_navigation_buttons(self):
        self.prev_button.config(state=tk.NORMAL if self.current_index > 0 else tk.DISABLED)
        self.next_button.config(state=tk.NORMAL if self.current_index < len(self.image_paths) - 1 else tk.DISABLED)
        

    def save_predictions(self):
        # Get the custom CSV filename
        output_filename = self.csv_filename_var.get()
        if not output_filename.endswith('.csv'):
            output_filename += '.csv'

        # Define the output folder and file
        output_folder = "results/files"
        os.makedirs(output_folder, exist_ok=True)
        output_file = os.path.join(output_folder, output_filename)

        # Load existing predictions from the CSV file
        existing_predictions = {}
        if os.path.exists(output_file):
            with open(output_file, mode='r', newline='') as csvfile:
                csv_reader = csv.reader(csvfile)
                next(csv_reader, None)  # Skip header
                for row in csv_reader:
                    if len(row) == 2:  # Ensure row has the correct format
                        existing_predictions[row[0]] = row[1]

        # Update existing predictions or add new ones
        for image_path, predicted_time in self.predictions:
            # Extract just the filename without extension
            image_name = os.path.splitext(os.path.basename(image_path))[0]
            existing_predictions[image_name] = predicted_time

        # Add "Time detection failed" cases to the CSV
        for image_path in self.image_paths:
            # Extract just the filename without extension
            image_name = os.path.splitext(os.path.basename(image_path))[0]
            if image_name not in existing_predictions:
                existing_predictions[image_name] = "failed"

        # Write the updated predictions back to the CSV file
        try:
            with open(output_file, mode='w', newline='') as csvfile:
                csv_writer = csv.writer(csvfile)
                csv_writer.writerow(["Image Name", "Predicted Time"])
                for image_name, predicted_time in existing_predictions.items():
                    csv_writer.writerow([image_name, predicted_time])
            messagebox.showinfo("Success", f"Predictions saved to {output_file}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save predictions: {e}")
            
    def calculate_time_deviation(self, predicted_time, ground_truth_time):
        """
        Calculate the absolute time difference in seconds between predicted and ground truth times.
        """
        if predicted_time == "failed" or ground_truth_time is None:
            return None
        
        try:
            # Split times into hours, minutes, seconds
            pred_parts = predicted_time.split(':')
            truth_parts = ground_truth_time.split(':')
            
            # Convert to total seconds
            pred_seconds = int(pred_parts[0]) * 3600 + int(pred_parts[1]) * 60 + (int(pred_parts[2]) if len(pred_parts) > 2 else 0)
            truth_seconds = int(truth_parts[0]) * 3600 + int(truth_parts[1]) * 60 + (int(truth_parts[2]) if len(truth_parts) > 2 else 0)
            
            # Calculate absolute deviation
            return abs(pred_seconds - truth_seconds)
        except (ValueError, IndexError):
            return None

    # Modified method to find ground truth for an image
    def find_ground_truth(self, image_name):
        """
        Search for ground truth time for a given image name in the ground truth CSV.
        """
        try:
            with open(self.ground_truth_path, mode='r') as file:
                csv_reader = csv.reader(file)
                for row in csv_reader:
                    if row[0] == image_name:
                        return row[1]
        except FileNotFoundError:
            print(f"Ground truth file {self.ground_truth_path} not found.")
        except Exception as e:
            print(f"Error reading ground truth file: {e}")
        return None
    
    def load_predictions(self):
        """
        Load predictions from the CSV file into memory.
        """
        output_filename = self.csv_filename_var.get()
        if not output_filename.endswith('.csv'):
            output_filename += '.csv'

        output_folder = "results/files"
        output_file = os.path.join(output_folder, output_filename)

        self.loaded_predictions.clear()
        if os.path.exists(output_file):
            try:
                with open(output_file, mode='r', newline='') as csvfile:
                    csv_reader = csv.reader(csvfile)
                    next(csv_reader, None)  # Skip header
                    for row in csv_reader:
                        if len(row) == 2:
                            self.loaded_predictions[row[0]] = row[1]
            except Exception as e:
                print(f"Error loading predictions: {e}")
                
    def display_image(self, image_path):
        try:
            # Define clock image path
            extracted_id = os.path.splitext(os.path.basename(image_path))[0]
            clock_final_path = f'results/images/{extracted_id}_clock.jpg'

            if os.path.exists(clock_final_path):
                final_pil_img = Image.open(clock_final_path)
            else:
                print(f"Clock image not found: {clock_final_path}")
                final_pil_img = Image.open(image_path)

            if final_pil_img:
                final_pil_img = final_pil_img.resize((215, 215), Image.LANCZOS)
                final_photo = ImageTk.PhotoImage(final_pil_img)
                self.original_image_label.config(image=final_photo, text="")
                self.original_image_label.image = final_photo
            else:
                self.original_image_label.config(image='', text="Clock Image Not Found")
            
            # Determine detection image path
            detection_path = os.path.join(
                'results', 'image_detections', f"{extracted_id}_detection.jpg"
            )

            # Display detection image if exists
            if os.path.exists(detection_path):
                print(f"Detection image found: {detection_path}")
                detection_pil_img = Image.open(detection_path)
                detection_pil_img = detection_pil_img.resize((215, 215), Image.LANCZOS)
                detection_photo = ImageTk.PhotoImage(detection_pil_img)
                self.detection_image_label.config(image=detection_photo, text="")
                self.detection_image_label.image = detection_photo
            else:
                print(f"No detection image found at: {detection_path}")
                self.detection_image_label.config(image='', text="No Detection Image")
        
        except Exception as e:
            print(f"Error displaying image: {e}")
            self.original_image_label.config(image='', text="Failed to load original image")
            self.detection_image_label.config(image='', text="Failed to load detection image")

    def select_ground_truth_csv(self):
        ground_truth_path = filedialog.askopenfilename(
        title="Select Ground Truth CSV",
        filetypes=[("CSV files", "*.csv")],
        initialdir="ground_truths"  # Optional: set an initial directory
        )
        if ground_truth_path:
            # Update the ground truth path variable
            self.ground_truth_path_var.set(ground_truth_path)
            # Also update the ground_truth_path attribute
            self.ground_truth_path = ground_truth_path
    
    

def main():
    root = ThemedTk(theme="Breeze")  
    app = ClockDetectionApp(root)
    root.mainloop()
if __name__ == "__main__":
    main()

