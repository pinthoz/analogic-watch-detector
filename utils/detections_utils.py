import os
import re
import json
from ultralytics import YOLO
import cv2
import numpy as np
import torch

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

def run_detection(
    image_path=None,
    model_path=None,
    confidence=0.01,
    save_path=None,
    zoom=False,
    model=None,
    image=None,
    save_visualization=True,
    return_prediction_results=False,
):
    """
    Run object detection on an image without Non-Maximum Suppression

    Args:
        image_path (str): Path to the input image
        model_path (str, optional): Path to the YOLO model weights
        confidence (float, optional): Initial confidence threshold
        save_path (str, optional): Path to save detection results JSON

    Returns:
        list: Detections from the image
    """
    # Find model path if not provided
    if image_path is None and image is None:
        raise ValueError("Either 'image_path' or 'image' must be provided for detection.")

    if model is None:
        if not model_path:
            model_path = os.path.join(get_latest_train_dir(), "weights/best.pt")
        model = YOLO(model_path)

    # Default save path if not specified
    image_identifier = (
        os.path.splitext(os.path.basename(image_path))[0]
        if image_path
        else "uploaded_image"
    )
    if not save_path and image_path:
        save_path = os.path.join('results/detections', f'{image_identifier}_detection.json')

    # Ensure detections directory exists
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
    if save_visualization and image_path:
        os.makedirs('results/image_detections', exist_ok=True)

    # Determine prediction source
    source = image if image is not None else image_path

    # Run detection
    results = model.predict(
        source=source,
        save=save_visualization,
        save_txt=False,
        conf=confidence,
        max_det=50,
        verbose=False,
    )

    # Convert detections to list format
    detections = []
    for result in results:
        # Extract raw detections
        boxes = result.boxes.xyxy.cpu().numpy()
        confidences = result.boxes.conf.cpu().numpy()
        classes = result.boxes.cls.cpu().numpy()

        # Get class names
        if hasattr(result.names, 'items'):
            class_names = {int(k): v for k, v in result.names.items()}
        else:
            class_names = {int(cls_id): str(cls_id) for cls_id in np.unique(classes)}

        # Create list of detections for this image
        image_detections = []
        for box, score, cls_id in zip(boxes, confidences, classes):
            cls_name = class_names.get(int(cls_id), "unknown")
            detection = {
                'box': box.tolist(),  # [x_min, y_min, x_max, y_max]
                'confidence': float(score),
                'class_id': int(cls_id),
                'class_name': cls_name
            }
            image_detections.append(detection)

        detections.append(image_detections)

    # Create a visualization only for detections with confidence > 0.1
    if save_visualization and results:
        filtered_results = results.copy()

        # Filtred results with confidence > 0.1
        filtered_results[0].boxes = filtered_results[0].boxes[filtered_results[0].boxes.conf > 0.1]

        # Plot the detections
        res_plotted = filtered_results[0].plot()

        output_path = f"results/image_detections/{image_identifier}_detection.jpg"
        cv2.imwrite(output_path, res_plotted)
        print(f"Imagem salva com as detecções em: results/image_detections/{image_identifier}")

    # Save to JSON file
    if save_path:
        with open(save_path, 'w') as f:
            json.dump(detections, f, indent=4)

        print(f"Detections saved to: {save_path}")

    if return_prediction_results:
        return detections, results

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

