import cv2
import math


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

def process_clock_time(detections_data, image_path):
    """Process clock time from detections"""
    # Organize detections by class_name and select the one with highest confidence for each class
    detections_by_class = {}
    for detection in detections_data[0]:
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

    # Calculate raw angles relative to 12 o'clock position
    hour_angle = calculate_angle(center_point, hours_point, number_12_point)
    minute_angle = calculate_angle(center_point, minutes_point, number_12_point)

    # Calculate seconds angle if seconds point exists
    if seconds_point:
        seconds_angle = calculate_angle(center_point, seconds_point, number_12_point)

    # Convert angles to time
    hours = (hour_angle / 30)  # Each hour is 30 degrees
    minutes = (minute_angle / 6)  # Each minute is 6 degrees

    # Round to nearest hour and minute
    hours = math.floor(hours) % 12
    if hours == 0:
        hours = 12
    minutes = math.floor(minutes) % 60
    
    # Calculate seconds if angle exists
    if seconds_angle is not None:
        seconds = (seconds_angle / 6)  # Each second is 6 degrees
        seconds = round(seconds) % 60
        calculated_seconds = seconds

    return {
        'hours': hours,
        'minutes': minutes,
        'seconds': calculated_seconds if seconds_angle is not None else None
    }

def draw_clock(image_path, center_point, hours_point, minutes_point, seconds_point, number_12_point, hour_angle, minute_angle, seconds_angle, calculated_hours, calculated_minutes, calculated_seconds, image_name):
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
    
    # Draw the lines with thicker strokes
    cv2.line(img, center, hours, (0, 0, 255), 5)     # Ponteiro das horas em vermelho (espessura maior)
    cv2.line(img, center, minutes, (255, 0, 0), 4)   # Ponteiro dos minutos em azul (espessura maior)
    if seconds:
        cv2.line(img, center, seconds, (255, 165, 0), 2)   # Ponteiro dos segundos em laranja (espessura maior)
    
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
    

    output_path = f'results/images/{image_name}'
    cv2.imwrite(output_path, img)
    print(f"Annotated image saved to {output_path}")
    
