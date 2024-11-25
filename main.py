import json
import math
import cv2
import numpy as np

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

def draw_clock_hands(image_path, center_point, hours_point, minutes_point, number_12_point, hour_angle, minute_angle, calculated_hours, calculated_minutes):
    """Draw clock hands and reference points on the image"""
    # Ler a imagem
    img = cv2.imread(image_path)
    
    # Converter pontos para inteiros (OpenCV requer coordenadas em int)
    center = (int(center_point[0]), int(center_point[1]))
    hours = (int(hours_point[0]), int(hours_point[1]))
    minutes = (int(minutes_point[0]), int(minutes_point[1]))
    twelve = (int(number_12_point[0]), int(number_12_point[1]))
    
    # Desenhar pontos de referência
    cv2.circle(img, center, 3, (0, 0, 255), -1)  # Centro em vermelho
    cv2.circle(img, twelve, 3, (255, 0, 0), -1)  # Ponto 12 em azul
    
    # Desenhar linhas dos ponteiros
    cv2.line(img, center, hours, (0, 0, 255), 2)     # Ponteiro das horas em vermelho
    cv2.line(img, center, minutes, (255, 0, 0), 2)   # Ponteiro dos minutos em azul
    cv2.line(img, center, twelve, (0, 255, 0), 1)    # Linha de referência (12h) em verde
    
    # Desenhar texto com informações
    cv2.putText(img, f"Hour angle: {hour_angle:.1f}", 
                (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    cv2.putText(img, f"Minute angle: {minute_angle:.1f}", 
                (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    cv2.putText(img, f"Time: {int(calculated_hours):02d}:{int(calculated_minutes):02d}", 
                (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    
    # Salvar e mostrar a imagem
    cv2.imwrite('clock_with_hands.jpg', img)
    
    # Mostrar a imagem
    cv2.imshow('Clock with hands', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# Leitura do JSON
with open("detections3.json", "r") as f:
    data = json.load(f)

# Extract centers for each component
boxes_dict = {box['class_name']: box['box'] for box in data[0]}

# Calculate centers
center_point = get_box_center(boxes_dict['center'])
hours_point = get_box_center(boxes_dict['hours'])
minutes_point = get_box_center(boxes_dict['minutes'])
number_12_point = get_box_center(boxes_dict['12'])

# Calculate clock radius
circle_box = boxes_dict['circle']
circle_radius = ((circle_box[2] - circle_box[0]) + (circle_box[3] - circle_box[1])) / 4

# Calculate raw angles relative to 12 o'clock position
hour_angle = calculate_angle(center_point, hours_point, number_12_point)
minute_angle = calculate_angle(center_point, minutes_point, number_12_point)

# Convert angles to time
hours = (hour_angle / 30)  # Each hour is 30 degrees
minutes = (minute_angle / 6)  # Each minute is 6 degrees

# Round to nearest hour/minute
hours = round(hours) % 12
if hours == 0:
    hours = 12
minutes = round(minutes) % 60

print(f"Clock center: {center_point}")
print(f"Hour angle: {hour_angle:.1f}°")
print(f"Minute angle: {minute_angle:.1f}°")
print(f"Time: {hours:02d}:{minutes:02d}")

# Chamar a função de desenho
image_path = "watch_test3.jpg"  # Substitua pelo caminho correto da sua imagem
draw_clock_hands(image_path, center_point, hours_point, minutes_point, number_12_point, hour_angle, minute_angle, hours, minutes)