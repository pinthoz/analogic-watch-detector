from ultralytics import YOLO
import cv2
import os
import re
import json
import numpy as np

def get_latest_train_dir(base_path="runs/detect"):
    """
    Encontra o diretório de treino mais recente (train, train1, train2, etc.)
    """
    if not os.path.exists(base_path):
        raise FileNotFoundError(f"O diretório {base_path} não existe")
    
    train_dirs = [d for d in os.listdir(base_path) 
                 if os.path.isdir(os.path.join(base_path, d)) and d.startswith('train')]
    
    if not train_dirs:
        raise FileNotFoundError("Nenhum diretório 'train' encontrado")
    
    def get_train_number(dirname):
        match = re.search(r'train(\d+)?$', dirname)
        if not match or not match.group(1):
            return -1
        return int(match.group(1))
    
    latest_train = max(train_dirs, key=get_train_number)
    return os.path.join(base_path, latest_train)

def save_detections(results, output_file="detections3.json"):
    """
    Salva as detecções em um arquivo JSON
    
    Args:
        results: Resultados da predição do YOLO
        output_file (str): Nome do arquivo para salvar as detecções
    """
    detections = []
    
    for result in results:
        boxes = result.boxes.xyxy.cpu().numpy().tolist()  # Converte para lista
        confidences = result.boxes.conf.cpu().numpy().tolist()
        classes = result.boxes.cls.cpu().numpy().tolist()
        
        # Obtém os nomes das classes se disponíveis
        if hasattr(result.names, 'items'):
            class_names = [result.names[int(cls_id)] for cls_id in classes]
        else:
            class_names = [str(int(cls_id)) for cls_id in classes]
        
        # Cria lista de detecções para esta imagem
        image_detections = []
        for box, conf, cls_id, cls_name in zip(boxes, confidences, classes, class_names):
            detection = {
                'box': box,  # [x_min, y_min, x_max, y_max]
                'confidence': conf,
                'class_id': cls_id,
                'class_name': cls_name
            }
            image_detections.append(detection)
        
        detections.append(image_detections)
    
    # Salva no arquivo JSON
    with open(output_file, 'w') as f:
        json.dump(detections, f, indent=4)
    
    print(f"Detecções salvas em: {output_file}")
    return detections

def load_detections(input_file="detections3.json"):
    """
    Carrega as detecções de um arquivo JSON
    
    Args:
        input_file (str): Nome do arquivo para carregar as detecções
        
    Returns:
        list: Lista de detecções
    """
    with open(input_file, 'r') as f:
        detections = json.load(f)
    return detections

# Uso principal
model_path = os.path.join(get_latest_train_dir(), "weights/best.pt")
model = YOLO(model_path)

# Caminho da imagem para inferência
image_path = "watch_test3.jpg"
output_path = "output3.jpg"

# Fazer a inferência
results = model.predict(source=image_path, save=True, save_txt=False)

# Salvar as detecções em um arquivo
detections = save_detections(results)

# Salvar a imagem com as detecções
cv2.imwrite(output_path, results[0].plot())
print(f"Imagem salva com as detecções em: {output_path}")

# Exemplo de como carregar e usar as detecções posteriormente
loaded_detections = load_detections()
print("\nDetecções carregadas:")
for img_detections in loaded_detections:
    for det in img_detections:
        print(f"Classe: {det['class_name']}")
        print(f"Box: {det['box']}")
        print(f"Confiança: {det['confidence']:.2f}")
        
        
import cv2
import numpy as np
import math
from scipy.stats import skew
from skimage.feature import graycomatrix, graycoprops
from skimage import filters
from ultralytics import YOLO

class ClockImageValidator:
    def __init__(self, debug=False):
        """
        Inicializa o validador de imagens de relógio
        
        Args:
            debug (bool): Se True, salva imagens intermediárias para análise
        """
        self.debug = debug
    
    def is_circular_shape(self, image, threshold=0.8):
        """
        Verifica se a imagem contém uma forma circular aproximada
        
        Args:
            image (np.ndarray): Imagem de entrada
            threshold (float): Limiar de circularidade
        
        Returns:
            bool: True se a forma for circular, False caso contrário
        """
        # Converte para escala de cinza
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Aplica blur para reduzir ruídos
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Detecção de bordas
        edges = cv2.Canny(blurred, 50, 200)
        
        # Encontra contornos
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Procura pelo maior contorno
        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            
            # Calcula a área do contorno e área do círculo equivalente
            contour_area = cv2.contourArea(largest_contour)
            perimeter = cv2.arcLength(largest_contour, True)
            
            # Compara circularidade
            if perimeter > 0:
                circularity = 4 * math.pi * contour_area / (perimeter ** 2)
                
                if self.debug:
                    print(f"Circularidade: {circularity}")
                    cv2.drawContours(image, [largest_contour], -1, (0, 255, 0), 2)
                    cv2.imwrite('circular_check.jpg', image)
                
                return circularity > threshold
        
        return False
    
    def check_clock_like_texture(self, image):
        """
        Analisa a textura da imagem para características de relógio
        
        Args:
            image (np.ndarray): Imagem de entrada
        
        Returns:
            bool: True se a textura for similar a um relógio
        """
        # Converte para escala de cinza
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Matriz de co-ocorrência de níveis de cinza
        glcm = graycomatrix(gray, distances=[1], angles=[0], levels=256,
                            symmetric=True, normed=True)
        
        # Extrai propriedades da textura
        properties = {
            'contrast': graycoprops(glcm, 'contrast')[0, 0],
            'dissimilarity': graycoprops(glcm, 'dissimilarity')[0, 0],
            'homogeneity': graycoprops(glcm, 'homogeneity')[0, 0],
            'energy': graycoprops(glcm, 'energy')[0, 0],
            'correlation': graycoprops(glcm, 'correlation')[0, 0]
        }
        
        # Valores típicos para texturas de relógios
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
        """
        Detecta a presença de ponteiros de relógio
        
        Args:
            image (np.ndarray): Imagem de entrada
        
        Returns:
            bool: True se ponteiros forem detectados
        """
        # Converte para escala de cinza
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Detecção de linhas usando Transformada de Hough
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, 100, minLineLength=50, maxLineGap=10)
        
        if lines is not None and len(lines) >= 2:
            # Verifica ângulos das linhas para características de ponteiros
            angles = [math.degrees(math.atan2(line[0][3] - line[0][1], line[0][2] - line[0][0])) for line in lines]
            
            # Analisa distribuição dos ângulos
            angle_skew = skew(angles)
            
            if self.debug:
                print(f"Número de linhas detectadas: {len(lines)}")
                print(f"Inclinação dos ângulos: {angle_skew}")
                
                # Desenha linhas detectadas
                line_image = image.copy()
                for line in lines:
                    x1, y1, x2, y2 = line[0]
                    cv2.line(line_image, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.imwrite('detected_lines.jpg', line_image)
            
            return len(lines) >= 2 and abs(angle_skew) < 1.5
        
        return False
    
    def validate_clock_image(self, image_path):
        """
        Valida se a imagem é de um relógio
        
        Args:
            image_path (str): Caminho da imagem
        
        Returns:
            bool: True se a imagem for validada como relógio
        """
        # Carrega a imagem
        image = cv2.imread(image_path)
        
        # Resize para processamento mais rápido
        image = cv2.resize(image, (600, 600))
        
        # Validações sequenciais
        checks = [
            self.is_circular_shape(image),
            self.check_clock_like_texture(image),
            self.detect_clock_hands(image)
        ]
        
        # Requer ao menos 2 de 3 validações
        validation_result = sum(checks) >= 2
        
        if self.debug:
            print("Resultados das Validações:")
            print(f"Forma Circular: {checks[0]}")
            print(f"Textura de Relógio: {checks[1]}")
            print(f"Ponteiros Detectados: {checks[2]}")
            print(f"Resultado Final: {'Válido' if validation_result else 'Inválido'}")
        
        return validation_result

# Exemplo de uso
def main():
    validator = ClockImageValidator(debug=True)
    
    # Caminho da imagem
    image_path = "watch_test3.jpg"
    
    # Valida a imagem
    is_valid_clock = validator.validate_clock_image(image_path)
    
    if is_valid_clock:
        print("Imagem válida! Processando...")
        # Aqui você chamaria seu processamento de detecção do relógio
    else:
        print("Imagem inválida. Não é um relógio.")

if __name__ == "__main__":
    main()