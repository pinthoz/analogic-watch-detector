import os
import re
import json
from ultralytics import YOLO
import cv2

def get_latest_train_dir(base_path="runs/detect"):
    """Find the most recent training directory (train, train1, train2, etc.)"""
    if not os.path.exists(base_path):
        raise FileNotFoundError(f"Directory {base_path} does not exist")
    
    train_dirs = [d for d in os.listdir(base_path) 
                  if os.path.isdir(os.path.join(base_path, d)) and d.startswith('train')]
    
    if not train_dirs:
        raise FileNotFoundError("No 'train' directory found")
    
    def get_train_number(dirname):
        match = re.search(r'train(\d+)?$', dirname)
        if not match or not match.group(1):
            return -1
        return int(match.group(1))
    
    latest_train = max(train_dirs, key=get_train_number)
    return os.path.join(base_path, latest_train)

def run_detection(image_path, model_path=None, confidence=0.5, save_path=None):
    """
    Run object detection on an image
    
    Args:
        image_path (str): Path to the input image
        model_path (str, optional): Path to the YOLO model weights
        confidence (float, optional): Confidence threshold
        save_path (str, optional): Path to save detection results JSON
    
    Returns:
        list: Detections from the image
    """
    # Find model path if not provided
    if not model_path:
        model_path = os.path.join(get_latest_train_dir(), "weights/best.pt")
    
    # Default save path if not specified
    if not save_path:
        save_path = os.path.join('detections', f'{os.path.splitext(os.path.basename(image_path))[0]}_detection.json')
    
    # Ensure detections directory exists
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    
    # Load model and run detection
    model = YOLO(model_path)
    results = model.predict(source=image_path, save=True, save_txt=False, conf=confidence)
    cv2.imwrite(f"examples/{os.path.splitext(os.path.basename(image_path))[0]}_detection.jpg", results[0].plot())
    print(f"Imagem salva com as detecções em: examples/{os.path.splitext(os.path.basename(image_path))[0]}")
    # Convert detections to list format
    detections = []
    for result in results:
        boxes = result.boxes.xyxy.cpu().numpy().tolist()
        confidences = result.boxes.conf.cpu().numpy().tolist()
        classes = result.boxes.cls.cpu().numpy().tolist()
        
        # Get class names
        if hasattr(result.names, 'items'):
            class_names = [result.names[int(cls_id)] for cls_id in classes]
        else:
            class_names = [str(int(cls_id)) for cls_id in classes]
        
        # Create list of detections for this image
        image_detections = []
        for box, conf, cls_id, cls_name in zip(boxes, confidences, classes, class_names):
            detection = {
                'box': box,  # [x_min, y_min, x_max, y_max]
                'confidence': float(conf),
                'class_id': int(cls_id),
                'class_name': cls_name
            }
            image_detections.append(detection)
        
        detections.append(image_detections)
    
    # Save to JSON file
    with open(save_path, 'w') as f:
        json.dump(detections, f, indent=4)
    
    print(f"Detections saved to: {save_path}")
    return detections

def load_detections(input_file):
    """
    Load detections from a JSON file
    
    Args:
        input_file (str): Path to the JSON detection file
        
    Returns:
        list: Loaded detections
    """
    with open(input_file, 'r') as f:
        detections = json.load(f)
    return detections