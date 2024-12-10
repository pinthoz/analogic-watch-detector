import os
import re
import json
from ultralytics import YOLO
import cv2
import numpy as np


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

def run_detection(image_path, model_path=r"C:\Users\anoca\Documents\GitHub\analogic-watch-detector\runs\detect\train57\weights\last.pt", confidence=0.01, save_path=None, nms_method=1, nms_sigma=0.5, zoom=False):
    """
    Run object detection on an image with Soft Non-Maximum Suppression
    
    Args:
        image_path (str): Path to the input image
        model_path (str, optional): Path to the YOLO model weights
        confidence (float, optional): Initial confidence threshold
        save_path (str, optional): Path to save detection results JSON
        nms_method (int, optional): Soft-NMS method (1: Gaussian, 2: Linear, 3: Hard)
        nms_sigma (float, optional): Gaussian decay parameter for Soft-NMS
    
    Returns:
        list: Detections from the image
    """
    # Find model path if not provided
    if not model_path:
        model_path = os.path.join(get_latest_train_dir(), "weights/best.pt")
    
    # Default save path if not specified
    if not save_path:
        save_path = os.path.join('results/detections', f'{os.path.splitext(os.path.basename(image_path))[0]}_detection.json')
    
    # Ensure detections directory exists
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    os.makedirs('results/image_detections', exist_ok=True)
    
    # Load model and run detection
    model = YOLO(model_path)
    results = model.predict(source=image_path, save=True, save_txt=False, conf=confidence, max_det=50)
    
    # Convert detections to list format and apply filtering
    detections = []
    for result in results:
        # Extract raw detections
        boxes = result.boxes.xyxy.cpu().numpy()
        confidences = result.boxes.conf.cpu().numpy()
        classes = result.boxes.cls.cpu().numpy()
        
        # Apply Soft-NMS
        soft_boxes, soft_scores, soft_classes = soft_nms(
            boxes, 
            confidences, 
            classes,
            confidence_threshold=0.01,  # Low threshold to start
            iou_threshold=0.5, 
            sigma=nms_sigma, 
            method=nms_method
        )
        
        # Get class names
        if hasattr(result.names, 'items'):
            class_names = {int(k): v for k, v in result.names.items()}
        else:
            class_names = {int(cls_id): str(cls_id) for cls_id in np.unique(classes)}

        # Create list of detections for this image
        image_detections = []
        for box, score, cls_id in zip(soft_boxes, soft_scores, soft_classes):
            cls_name = class_names.get(int(cls_id), "unknown")
            detection = {
                'box': box.tolist(),  # [x_min, y_min, x_max, y_max]
                'confidence': float(score),
                'class_id': int(cls_id),
                'class_name': cls_name
            }
            image_detections.append(detection)
        
        detections.append(image_detections)
        
    
    # Create a visualization with soft-NMS detections
    if results:
        res_plotted = results[0].plot()
        cv2.imwrite(f"results/image_detections/{os.path.splitext(os.path.basename(image_path))[0]}_detection.jpg", res_plotted)
        print(f"Imagem salva com as detecções em: results/image_detections/{os.path.splitext(os.path.basename(image_path))[0]}")

    
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

def soft_nms(boxes, scores, classes, confidence_threshold=0.01, iou_threshold=0.5, sigma=0.5, method=1):
    """
    Soft Non-Maximum Suppression with multiple detection support
    
    Args:
        boxes (np.ndarray): Detection bounding boxes (N, 4)
        scores (np.ndarray): Detection confidence scores (N,)
        classes (np.ndarray): Detection class IDs (N,)
        confidence_threshold (float): Minimum confidence to keep a detection
        iou_threshold (float): IoU threshold for suppression
        sigma (float): Gaussian decay parameter
        method (int): NMS method (1: Gaussian, 2: Linear, 3: Hard)
    
    Returns:
        tuple: Filtered boxes, scores, and classes
    """
    # Sort detections by confidence
    sorted_indices = np.argsort(scores)[::-1]
    boxes = boxes[sorted_indices]
    scores = scores[sorted_indices]
    classes = classes[sorted_indices]

    def iou(box1, box2):
        """Compute Intersection over Union"""
        x1 = max(box1[0], box2[0])
        y1 = max(box1[1], box2[1])
        x2 = min(box1[2], box2[2])
        y2 = min(box1[3], box2[3])
        
        inter_area = max(0, x2 - x1) * max(0, y2 - y1)
        
        box1_area = (box1[2] - box1[0]) * (box1[3] - box1[1])
        box2_area = (box2[2] - box2[0]) * (box2[3] - box2[1])
        
        union_area = box1_area + box2_area - inter_area
        
        return inter_area / union_area if union_area > 0 else 0

    # Initialize keep and suppressed flags
    keep = []
    suppressed = np.zeros(len(scores), dtype=bool)

    for i in range(len(scores)):
        # Skip if already suppressed or below confidence threshold
        if suppressed[i] or scores[i] < confidence_threshold:
            continue

        # Keep this detection
        keep.append(i)

        # Compare with subsequent detections
        for j in range(i + 1, len(scores)):
            if suppressed[j]:
                continue

            # Compute IoU
            curr_iou = iou(boxes[i], boxes[j])

            # Apply suppression based on method
            if curr_iou > iou_threshold:
                if method == 1:  # Gaussian
                    scores[j] *= np.exp(-(curr_iou * curr_iou) / sigma)
                elif method == 2:  # Linear
                    scores[j] *= max(0, 1 - curr_iou)
                else:  # Hard NMS
                    if curr_iou > iou_threshold:
                        suppressed[j] = True

                # Mark as suppressed if score drops too low
                if scores[j] < confidence_threshold:
                    suppressed[j] = True

    # Return filtered detections
    keep_indices = np.array(keep)
    return boxes[keep_indices], scores[keep_indices], classes[keep_indices]