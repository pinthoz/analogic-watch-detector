from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import io
import base64
import cv2
import numpy as np
from pathlib import Path
import tempfile
import os
import uvicorn
# clock detection functions
from utils.detections_utils import run_detection
from utils.clock_utils import process_clock_time, draw_clock, get_box_center, calculate_angle

app = FastAPI()

def encode_image_to_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    except Exception as e:
        print(f"Error encoding image: {e}")
        return None

def draw_clock_visualization(image_path, detections_by_class, result, output_path):
    """Helper function to generate clock visualization"""
    try:
        # Read the original image
        img = cv2.imread(image_path)
        if img is None:
            print(f"Failed to read image at {image_path}")
            return False

        circle_box_point = get_box_center(detections_by_class['circle']['box'])
        center_point = get_box_center(detections_by_class['center']['box']) if 'center' in detections_by_class else circle_box_point
        hours_point = get_box_center(detections_by_class['hours']['box'])
        number_12_point = get_box_center(detections_by_class['12']['box'])
        minutes_point = get_box_center(detections_by_class['minutes']['box']) if 'minutes' in detections_by_class else None
        seconds_point = get_box_center(detections_by_class['seconds']['box']) if 'seconds' in detections_by_class else None

        # Convert points to integers
        center = (int(center_point[0]), int(center_point[1]))
        hours = (int(hours_point[0]), int(hours_point[1]))
        twelve = (int(number_12_point[0]), int(number_12_point[1]))

        # Draw reference points
        cv2.circle(img, center, 3, (0, 0, 255), -1)  # Center in red
        cv2.circle(img, twelve, 3, (255, 0, 0), -1)  # 12 o'clock in blue

        # Draw hour hand
        cv2.line(img, center, hours, (0, 0, 255), 2)

        # Draw minute hand if exists
        if minutes_point:
            minutes = (int(minutes_point[0]), int(minutes_point[1]))
            cv2.line(img, center, minutes, (255, 0, 0), 2)

        # Draw second hand if exists
        if seconds_point:
            seconds = (int(seconds_point[0]), int(seconds_point[1]))
            cv2.line(img, center, seconds, (0, 255, 0), 1)

        # Add time text
        time_str = f"{result['hours']:02d}:{result.get('minutes', 0):02d}"
        if result.get('seconds') is not None:
            time_str += f":{result['seconds']:02d}"
        cv2.putText(img, f"Time: {time_str}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

        # Save the visualization
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        cv2.imwrite(output_path, img)
        return os.path.exists(output_path)
    except Exception as e:
        print(f"Error in draw_clock_visualization: {e}")
        return False

@app.post("/api/detect-time")
async def detect_time(file: UploadFile = File(...)):
    try:
        # Create temporary directory for processing
        temp_dir = tempfile.mkdtemp()

        # Read and validate the uploaded image
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))

        # Save to temporary file for processing
        temp_path = os.path.join(temp_dir, "input.jpg")
        image.save(temp_path)

        # Create results directories
        results_dir = os.path.join(temp_dir, "results")
        os.makedirs(os.path.join(results_dir, "images"), exist_ok=True)
        os.makedirs(os.path.join(results_dir, "image_detections"), exist_ok=True)

        # Run detection
        detections = run_detection(temp_path, confidence=0.01, 
                                   save_path=os.path.join(results_dir, "detections.json"))

        # Process clock time
        try:
            result = process_clock_time(detections, temp_path)
        except KeyError as e:
            raise HTTPException(
                status_code=400, 
                detail={
                    "message": "Error processing clock time",
                    "technical_details": f"Elements not detected: {str(e)}"
                }
            )
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "Error processing clock time",
                    "technical_details": str(e)
                }
            )

        if not result:
            raise HTTPException(
                status_code=400, 
                detail={
                    "message": "It was not possible to process the clock time",
                    "technical_details": "No clock elements detected"
                }
            )

        # Calculate confidence scores
        confidence_scores = []
        detection_classes = ['hours', 'minutes', 'seconds', 'center', '12']

        for detection in detections[0]:
            if detection['class_name'] in detection_classes:
                confidence_scores.append(detection['confidence'])

        # Calculate average confidence
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0

        # Generate detection visualization
        detections_by_class = {}
        for detection in detections[0]:
            class_name = detection['class_name']
            if class_name not in detections_by_class or detection['confidence'] > detections_by_class[class_name]['confidence']:
                detections_by_class[class_name] = detection

        detection_image = None
        if all(key in detections_by_class for key in ['hours', '12', 'circle']):
            viz_path = os.path.join(results_dir, "images", "detection_viz.jpg")

            # Generate visualization using the new helper function
            if draw_clock_visualization(temp_path, detections_by_class, result, viz_path):
                detection_image = encode_image_to_base64(viz_path)

        # Clean up temporary files
        try:
            import shutil
            shutil.rmtree(temp_dir)
        except Exception as e:
            print(f"Error cleaning up temporary files: {e}")

        return JSONResponse({
            "time": {
                "hours": result['hours'],
                "minutes": result.get('minutes', 0),
                "seconds": result.get('seconds', 0)
            },
            "confidence": avg_confidence,
            "detectionImage": f"data:image/jpeg;base64,{detection_image}" if detection_image else None
        })

    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail={
                "message": "Error processing image",
                "technical_details": str(e)
            }
    )

    
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # URL do seu frontend React
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)