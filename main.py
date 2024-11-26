import json
import math
import cv2
import numpy as np
import argparse
import sys
import os

def get_box_center(box):
    """Calculate the center point of a bounding box"""
    x = (box[0] + box[2]) / 2
    y = (box[1] + box[3]) / 2
    return (x, y)

def calculate_angle(center, point, reference_point):
    """Calculate angle between two points relative to 12 o'clock position"""
    # Calculate vectors
    ref_vector = (reference_point[0] - center[0], reference_point[1] - center[1])
    point_vector = (point[0] - center[0], point[1] - center[1])
    
    # Calculate angles from vectors
    ref_angle = math.atan2(ref_vector[1], ref_vector[0])
    point_angle = math.atan2(point_vector[1], point_vector[0])
    
    # Calculate relative angle in degrees
    angle = math.degrees(point_angle - ref_angle)
    
    # Normalize angle to 0-360 range
    angle = (angle + 360) % 360
    
    return angle

def draw_clock(image_path, center_point, hours_point, minutes_point, seconds_point, number_12_point, hour_angle, minute_angle, seconds_angle, calculated_hours, calculated_minutes, calculated_seconds):
    """Draw clock and reference points on the image"""

    img = cv2.imread(image_path)
    
    # To int
    center = (int(center_point[0]), int(center_point[1]))
    hours = (int(hours_point[0]), int(hours_point[1]))
    minutes = (int(minutes_point[0]), int(minutes_point[1]))
    seconds = (int(seconds_point[0]), int(seconds_point[1])) if seconds_point else None
    twelve = (int(number_12_point[0]), int(number_12_point[1]))
    
    # Draw the reference points
    cv2.circle(img, center, 3, (0, 0, 255), -1)  # Centro em vermelho
    cv2.circle(img, twelve, 3, (255, 0, 0), -1)  # Ponto 12 em azul
    
    # Draw the lines
    cv2.line(img, center, hours, (0, 0, 255), 2)     # Ponteiro das horas em vermelho
    cv2.line(img, center, minutes, (255, 0, 0), 2)   # Ponteiro dos minutos em azul
    if seconds:
        cv2.line(img, center, seconds, (0, 255, 0), 1)   # Ponteiro dos segundos em verde
    
    cv2.line(img, center, twelve, (0, 255, 0), 1)    # Linha de referência (12h) em verde
    
    # Draw the text
    cv2.putText(img, f"Hour angle: {hour_angle:.1f}", 
                (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    cv2.putText(img, f"Minute angle: {minute_angle:.1f}", 
                (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    
    if seconds_angle is not None:
        cv2.putText(img, f"Seconds angle: {seconds_angle:.1f}", 
                    (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        time_text = f"Time: {int(calculated_hours):02d}:{int(calculated_minutes):02d}:{int(calculated_seconds):02d}"
    else:
        time_text = f"Time: {int(calculated_hours):02d}:{int(calculated_minutes):02d}"
    
    cv2.putText(img, time_text, 
                (10, 120 if seconds else 90), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    
    # Salvar e mostrar a imagem
    output_path = 'clock_final.jpg'
    cv2.imwrite(output_path, img)
    print(f"Annotated image saved to {output_path}")
    
    # Mostrar a imagem
    cv2.imshow('Clock Final', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def process_clock_time(json_path, image_path):
    # Validate input files
    if not os.path.exists(json_path):
        print(f"Error: JSON file {json_path} not found.")
        return None
    
    if not os.path.exists(image_path):
        print(f"Error: Image file {image_path} not found.")
        return None

    # JSON
    with open(json_path, "r") as f:
        data = json.load(f)

    # Organize detections by class_name and select the one with highest confidence for each class
    detections_by_class = {}
    for detection in data[0]:
        class_name = detection['class_name']
        if class_name not in detections_by_class or detection['confidence'] > detections_by_class[class_name]['confidence']:
            detections_by_class[class_name] = detection

    # Validate required keys
    required_keys = ['hours', 'minutes', '12', 'circle']
    for key in required_keys:
        if key not in detections_by_class:
            print(f"Error: Missing required key '{key}' in detection data.")
            return None

    # Calculate circle center
    circle_box_point = get_box_center(detections_by_class['circle']['box'])
    
    # Determine center point: use 'center' if exists, otherwise use circle center
    if 'center' in detections_by_class:
        center_point = get_box_center(detections_by_class['center']['box'])
    else:
        center_point = circle_box_point

    hours_point = get_box_center(detections_by_class['hours']['box'])
    minutes_point = get_box_center(detections_by_class['minutes']['box'])
    number_12_point = get_box_center(detections_by_class['12']['box'])

    # Try to get seconds point with highest confidence
    seconds_point = None
    seconds_angle = None
    calculated_seconds = 0

    if 'seconds' in detections_by_class:
        seconds_point = get_box_center(detections_by_class['seconds']['box'])

    # Calculate clock radius
    circle_box = detections_by_class['circle']['box']
    circle_radius = ((circle_box[2] - circle_box[0]) + (circle_box[3] - circle_box[1])) / 4

    # Calculate raw angles relative to 12 o'clock position
    hour_angle = calculate_angle(center_point, hours_point, number_12_point)
    minute_angle = calculate_angle(center_point, minutes_point, number_12_point)

    # Calculate seconds angle if seconds point exists
    if seconds_point:
        seconds_angle = calculate_angle(center_point, seconds_point, number_12_point)

    # Convert angles to time
    hours = (hour_angle / 30)  # Each hour is 30 degrees
    minutes = (minute_angle / 6)  # Each minute is 6 degrees

    # Round to nearest hour/minute
    hours = round(hours) % 12
    if hours == 0:
        hours = 12
    minutes = round(minutes) % 60

    # Calculate seconds if angle exists
    if seconds_angle is not None:
        seconds = (seconds_angle / 6)  # Each second is 6 degrees
        seconds = round(seconds) % 60
        calculated_seconds = seconds

    print(f"Clock center: {center_point}")
    print(f"Hour angle: {hour_angle:.1f}°")
    print(f"Minute angle: {minute_angle:.1f}°")
    
    if seconds_angle is not None:
        print(f"Seconds angle: {seconds_angle:.1f}°")
        print(f"Time: {hours:02d}:{minutes:02d}:{calculated_seconds:02d}")
    else:
        print(f"Time: {hours:02d}:{minutes:02d}")

    # Call draw_clock with seconds parameters
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
        hours, 
        minutes, 
        calculated_seconds
    )

    return {
        'hours': hours,
        'minutes': minutes,
        'seconds': calculated_seconds if seconds_angle is not None else None
    }

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Clock Time Detection from Image')
    parser.add_argument('-j', '--json', 
                        help='Path to JSON detection file', 
                        default='detections/detections7.json')
    parser.add_argument('-i', '--image', 
                        help='Path to clock image', 
                        default='examples/watch_test7.jpg')
    
    # Parse arguments
    args = parser.parse_args()

    try:
        # Process the clock time
        result = process_clock_time(args.json, args.image)
        
        if result:
            print("\nClock Time Detection Completed Successfully!")
            if result['seconds'] is not None:
                print(f"Detected Time: {result['hours']:02d}:{result['minutes']:02d}:{result['seconds']:02d}")
            else:
                print(f"Detected Time: {result['hours']:02d}:{result['minutes']:02d}")
        else:
            print("Clock time detection failed.")
            sys.exit(1)

    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()