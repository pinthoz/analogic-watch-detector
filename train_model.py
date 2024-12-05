import optuna
from ultralytics import YOLO

def custom_metric(results):
    """
    Calcula a métrica: número total de imagens / número de classes detectadas corretamente.
    """
    # Ajuste conforme o formato real de `results`
    total_images = results["metrics"]["Images"]  # Total de imagens (substitua pelo acesso correto)
    class_metrics = results["class_metrics"]    # Métricas por classe (substitua pelo acesso correto)

    # Classes detectadas corretamente (Precision > 0 e Recall > 0)
    classes_detected = sum(
        1 for class_name, metrics in class_metrics.items()
        if metrics["precision"] > 0 and metrics["recall"] > 0
    )

    if classes_detected == 0:  # Evitar divisão por zero
        return 0

    return total_images / classes_detected

def objective(trial):
    # Sugerir valores para os hiperparâmetros
    lr = trial.suggest_loguniform("lr0", 1e-4, 1e-2)
    momentum = trial.suggest_uniform("momentum", 0.85, 0.95)
    weight_decay = trial.suggest_loguniform("weight_decay", 1e-5, 1e-3)

    # Carregar modelo YOLO
    model = YOLO("yolo11n.pt")

    # Treinamento do modelo
    results = model.train(
        data="dataset.yaml",
        epochs=10,  
        batch=16,
        imgsz=640,
        lr0=lr,
        momentum=momentum,
        weight_decay=weight_decay,
        device=0
    )

    # Capturar métricas
    metrics = results['metrics']
    precision = metrics['precision']
    recall = metrics['recall']
    map50 = metrics['mAP50']
    map95 = metrics['mAP50-95']

    # Combinar métricas para avaliação (ou retornar uma específica)
    return (map50 + map95 + precision + recall) / 4  # Média ponderada de métricas




if __name__ == "__main__":
    # Configurar o estudo do Optuna
    study = optuna.create_study(direction="maximize")
    study.optimize(objective, n_trials=20)  # 20 experimentos de tuning
    
    # Mostrar os melhores hiperparâmetros encontrados
    print("Melhores hiperparâmetros:", study.best_params)

    # Usar os melhores hiperparâmetros para treinamento completo
    best_params = study.best_params
    model = YOLO("yolo11n.pt")
    results = model.train(
        data="dataset.yaml",
        epochs=100,               # Treinamento completo
        batch=16,
        imgsz=640,
        lr0=best_params["lr0"],
        momentum=best_params["momentum"],
        weight_decay=best_params["weight_decay"],
        device=0
    )
