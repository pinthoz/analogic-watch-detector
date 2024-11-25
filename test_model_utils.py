import os
import re
from ultralytics import YOLO
import logging

class ModelManager:
    """
    Gerencia carregamento e seleção de modelos treinados
    """
    def __init__(self, base_path="runs/detect", logger=None):
        """
        Inicializa o gerenciador de modelos
        
        Args:
            base_path (str): Caminho base para treinamentos
            logger (logging.Logger): Logger para registro de eventos
        """
        self.base_path = base_path
        self.logger = logger or logging.getLogger(__name__)
    
    def get_latest_train_dir(self):
        """
        Encontra o diretório de treino mais recente
        
        Returns:
            str: Caminho do diretório de treino mais recente
        """
        try:
            # Verifica existência do diretório base
            if not os.path.exists(self.base_path):
                raise FileNotFoundError(f"O diretório {self.base_path} não existe")
            
            # Lista diretórios de treino
            train_dirs = [
                d for d in os.listdir(self.base_path) 
                if os.path.isdir(os.path.join(self.base_path, d)) 
                and d.startswith('train')
            ]
            
            if not train_dirs:
                raise FileNotFoundError("Nenhum diretório 'train' encontrado")
            
            def get_train_number(dirname):
                match = re.search(r'train(\d+)?$', dirname)
                return int(match.group(1)) if match and match.group(1) else -1
            
            latest_train = max(train_dirs, key=get_train_number)
            full_path = os.path.join(self.base_path, latest_train)
            
            self.logger.info(f"Diretório de treino mais recente: {full_path}")
            return full_path
        
        except Exception as e:
            self.logger.error(f"Erro ao encontrar diretório de treino: {e}")
            raise
    
    def load_model(self, weights_path=None):
        """
        Carrega modelo YOLO
        
        Args:
            weights_path (str, opcional): Caminho específico para pesos
        
        Returns:
            YOLO: Modelo carregado
        """
        try:
            if not weights_path:
                weights_path = os.path.join(self.get_latest_train_dir(), "weights/best.pt")
            
            model = YOLO(weights_path)
            self.logger.info(f"Modelo carregado de: {weights_path}")
            return model
        
        except Exception as e:
            self.logger.error(f"Erro ao carregar modelo: {e}")
            raise