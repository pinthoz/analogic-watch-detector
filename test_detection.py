import json
import cv2
import numpy as np
import logging
from typing import List, Dict
import os

class ClockDetector:
    """
    Classe para processamento de detecções de relógios
    """
    def __init__(self, model, logger=None):
        """
        Inicializa o detector
        
        Args:
            model: Modelo YOLO pré-treinado
            logger (logging.Logger): Logger para registro
        """
        self.model = model
        self.logger = logger or logging.getLogger(__name__)
    
    def detect(self, image_path: str, output_dir: str = 'examples/output'):
        """
        Realiza detecção em uma imagem
        
        Args:
            image_path (str): Caminho da imagem
            output_dir (str): Diretório para salvar resultados
        
        Returns:
            dict: Resultados da detecção
        """
        try:
            # Criar diretório de saída se não existir
            os.makedirs(output_dir, exist_ok=True)
            
            # Caminho para imagem de saída
            output_path = os.path.join(output_dir, 'detected_image.jpg')
            
            # Fazer inferência
            results = self.model.predict(
                source=image_path, 
                save=False, 
                save_txt=False
            )
            
            # Processar detecções
            detections = self._process_detections(results)
            
            # Salvar imagem com detecções
            cv2.imwrite(output_path, results[0].plot())
            
            self.logger.info(f"Detecções processadas para {image_path}")
            
            return {
                'detections': detections,
                'output_image': output_path
            }
        
        except Exception as e:
            self.logger.error(f"Erro na detecção: {e}")
            raise
    
    def _process_detections(self, results) -> List[Dict]:
        """
        Processa os resultados da detecção
        
        Args:
            results: Resultados do modelo YOLO
        
        Returns:
            List[Dict]: Lista de detecções processadas
        """
        detections = []
        
        for result in results:
            # Converte para numpy e lista
            boxes = result.boxes.xyxy.cpu().numpy().tolist()
            confidences = result.boxes.conf.cpu().numpy().tolist()
            classes = result.boxes.cls.cpu().numpy().tolist()
            
            # Obtém nomes das classes
            class_names = [
                result.names.get(int(cls_id), str(int(cls_id))) 
                for cls_id in classes
            ]
            
            # Cria lista de detecções
            image_detections = [{
                'box': box,
                'confidence': conf,
                'class_id': cls_id,
                'class_name': cls_name
            } for box, conf, cls_id, cls_name in zip(boxes, confidences, classes, class_names)]
            
            detections.extend(image_detections)
        
        return detections
    
    def save_detections(self, detections: List[Dict], output_file: str = 'detections4.json'):
        """
        Salva as detecções em arquivo JSON
        
        Args:
            detections (List[Dict]): Lista de detecções
            output_file (str): Arquivo de saída
        """
        try:
            with open(output_file, 'w') as f:
                json.dump(detections, f, indent=4)
            
            self.logger.info(f"Detecções salvas em: {output_file}")
        
        except Exception as e:
            self.logger.error(f"Erro ao salvar detecções: {e}")
            raise