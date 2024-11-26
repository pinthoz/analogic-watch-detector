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

def save_detections(results, output_file="detections/detections7.json"):
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

def load_detections(input_file="detections/detections7.json"):
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

image_path = "examples/watch_test7.jpg"
output_path = "examples/output7.jpg"

# Fazer o predict
results = model.predict(source=image_path, save=True, save_txt=False, conf = 0.5)

# Salvar as detecções em um arquivo
detections = save_detections(results)

# Salvar a imagem com as detecções
cv2.imwrite(output_path, results[0].plot())
print(f"Imagem salva com as detecções em: {output_path}")


loaded_detections = load_detections()
print("\nDetecções carregadas:")
for img_detections in loaded_detections:
    for det in img_detections:
        print(f"Classe: {det['class_name']}")
        print(f"Box: {det['box']}")
        print(f"Confiança: {det['confidence']:.2f}")
        
        