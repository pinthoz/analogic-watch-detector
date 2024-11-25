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

    def is_circular_shape(self, image, threshold=0.8):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 200)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            contour_area = cv2.contourArea(largest_contour)
            perimeter = cv2.arcLength(largest_contour, True)

            if perimeter > 0:
                circularity = 4 * math.pi * contour_area / (perimeter ** 2)

                if self.debug:
                    print(f"Circularidade: {circularity}")
                    cv2.drawContours(image, [largest_contour], -1, (0, 255, 0), 2)
                    cv2.imwrite('circular_check.jpg', image)

                return circularity > threshold

        return False
    
    
    def check_clock_like_texture(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        glcm = graycomatrix(gray, distances=[1], angles=[0], levels=256, symmetric=True, normed=True)

        properties = {
            'contrast': graycoprops(glcm, 'contrast')[0, 0],
            'dissimilarity': graycoprops(glcm, 'dissimilarity')[0, 0],
            'homogeneity': graycoprops(glcm, 'homogeneity')[0, 0],
            'energy': graycoprops(glcm, 'energy')[0, 0],
            'correlation': graycoprops(glcm, 'correlation')[0, 0]
        }

        clock_like_thresholds = {
            'contrast': (10, 50),
            'dissimilarity': (0.1, 0.5),
            'homogeneity': (0.3, 0.7),
            'energy': (0.1, 0.4),
            'correlation': (0.2, 0.8)
        }

        texture_score = sum(
            prop_range[0] <= properties[prop] <= prop_range[1]
            for prop, prop_range in clock_like_thresholds.items()
        )

        if self.debug:
            print("Propriedades de Textura:", properties)
            print(f"Escore de Textura de Relógio: {texture_score}/5")

        return texture_score >= 3

    def detect_clock_hands(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, 100, minLineLength=50, maxLineGap=10)

        if lines is not None and len(lines) >= 2:
            angles = [math.degrees(math.atan2(line[0][3] - line[0][1], line[0][2] - line[0][0])) for line in lines]
            angle_skew = skew(angles)

            if self.debug:
                print(f"Número de linhas detectadas: {len(lines)}")
                print(f"Inclinação dos ângulos: {angle_skew}")

                line_image = image.copy()
                for line in lines:
                    x1, y1, x2, y2 = line[0]
                    cv2.line(line_image, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.imwrite('detected_lines.jpg', line_image)

            return len(lines) >= 2 and abs(angle_skew) < 1.5

        return False

    def validate_clock_image(self, image_path):
        image = cv2.imread(image_path)
        image = cv2.resize(image, (600, 600))

        checks = [
            self.is_circular_shape(image),
            self.check_clock_like_texture(image),
            self.detect_clock_hands(image)
        ]

        # Mesmo que a imagem não passe em 2 ou mais verificações, ainda a consideraremos um relógio
        validation_result = sum(checks) >= 1

        if self.debug:
            print("Resultados das Validações:")
            print(f"Forma Circular: {checks[0]}")
            print(f"Textura de Relógio: {checks[1]}")
            print(f"Ponteiros Detectados: {checks[2]}")
            print(f"Resultado Final: {'Válido' if validation_result else 'Inválido'}")

        return validation_result

def main():
    validator = ClockImageValidator(debug=True)
    image_path = "examples/watch_test3.jpg"
    is_valid_clock = validator.validate_clock_image(image_path)

    if is_valid_clock:
        print("Imagem válida! Processando...")
    else:
        print("Imagem inválida. Não é um relógio.")

if __name__ == "__main__":
    main()