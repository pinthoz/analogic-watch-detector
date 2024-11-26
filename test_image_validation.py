import cv2
import numpy as np
import math
from scipy.stats import skew
from skimage.feature import graycomatrix, graycoprops
from skimage import filters
from ultralytics import YOLO

class ClockImageValidator:
    def __init__(self, debug=False):
        self.debug = debug

    def detect_clock_border_and_center(self, image):
        """
        Detect clock border and center using a focused region and optimized Hough parameters
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Crop the center region (reduce noise from the external areas)
        h, w = gray.shape
        cropped = gray[h // 4:h * 3 // 4, w // 4:w * 3 // 4]

        # Apply Bilateral Filter and Gaussian Blur
        blurred = cv2.bilateralFilter(cropped, 9, 75, 75)
        blurred = cv2.GaussianBlur(blurred, (5, 5), 0)
        
        # Apply Canny Edge Detection
        edges = cv2.Canny(blurred, 50, 150)
        
        if self.debug:
            cv2.imwrite('cropped_edges.jpg', edges)
        
        # Circle Hough Transform
        circles = cv2.HoughCircles(
            edges, 
            cv2.HOUGH_GRADIENT, 
            dp=1.2, 
            minDist=30, 
            param1=50, 
            param2=40, 
            minRadius=50, 
            maxRadius=150
        )
        
        if circles is not None:
            # Select the circle closest to the center of the cropped region
            circles = np.uint16(np.around(circles))
            center_crop = (cropped.shape[1] // 2, cropped.shape[0] // 2)
            best_circle = min(circles[0, :], key=lambda c: self._distance_point_to_point((c[0], c[1]), center_crop))
            
            # Adjust the circle coordinates back to the original image
            center = (best_circle[0] + w // 4, best_circle[1] + h // 4)
            radius = best_circle[2]
            
            if self.debug:
                debug_image = image.copy()
                cv2.circle(debug_image, center, radius, (0, 255, 0), 2)
                cv2.circle(debug_image, center, 2, (0, 0, 255), 3)
                cv2.imwrite('refined_circle_detection.jpg', debug_image)
            
            return center, radius
        
        return None, None

    def detect_clock_hands(self, image, center):
        """
        Detect clock hands using Probabilistic Hough Transform
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply Bilateral Filter to reduce noise
        filtered = cv2.bilateralFilter(gray, 9, 75, 75)
        
        # Apply Canny Edge Detection
        edges = cv2.Canny(filtered, 50, 150, apertureSize=3)
        
        # Probabilistic Hough Transform
        lines = cv2.HoughLinesP(
            edges, 
            1, 
            np.pi/180, 
            threshold=100, 
            minLineLength=50, 
            maxLineGap=10
        )
        
        if lines is not None:
            # Filter lines close to the center
            valid_lines = []
            for line in lines:
                x1, y1, x2, y2 = line[0]
                line_center_dist = self._distance_point_to_point((x1, y1), center)
                
                # Check if either line endpoint is close to the center
                if line_center_dist < 50:  # Adjust threshold as needed
                    valid_lines.append(line)
            
            if self.debug:
                debug_image = image.copy()
                for line in valid_lines:
                    x1, y1, x2, y2 = line[0]
                    cv2.line(debug_image, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.imwrite('clock_hands_detection.jpg', debug_image)
            
            return valid_lines
        
        return []

    def _distance_point_to_point(self, point1, point2):
        """
        Calculate Euclidean distance between two points
        """
        return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)

    def validate_clock_image(self, image_path):
        """
        Comprehensive clock image validation
        """
        # Read and resize image
        image = cv2.imread(image_path)
        image = cv2.resize(image, (600, 600))

        # Detect clock border and center
        center, radius = self.detect_clock_border_and_center(image)
        
        if center is None:
            if self.debug:
                print("No circular shape detected")
            return False

        # Detect clock hands
        clock_hands = self.detect_clock_hands(image, center)

        # Additional existing validations
        checks = [
            center is not None,  # Circular shape check
            len(clock_hands) >= 2  # At least two clock hands
        ]

        validation_result = sum(checks) == len(checks)

        if self.debug:
            print("Validation Results:")
            print(f"Circle Detected: {checks[0]}")
            print(f"Clock Hands Detected: {checks[1]}")
            print(f"Final Result: {'Valid' if validation_result else 'Invalid'}")

        return validation_result

def main():
    validator = ClockImageValidator(debug=True)
    image_path = "examples/watch_test.jpg"
    is_valid_clock = validator.validate_clock_image(image_path)

    if is_valid_clock:
        print("Valid image! Processing...")
    else:
        print("Invalid image. Not a clock.")

if __name__ == "__main__":
    main()