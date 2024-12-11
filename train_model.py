import yaml
from ultralytics import YOLO

def main():
    
    file_path = "runs/detect/tune4/best_hyperparameters.yaml"

    
    with open(file_path, 'r') as file:
        hyperparameters = yaml.safe_load(file)

    print(hyperparameters)

    model = YOLO('yolov8s.pt')
    model.train(
        data='dataset.yaml',
        **hyperparameters,
        imgsz=768,
        batch=16,
        device=0,
        optimizer='adamw',
        plots=True,
        save=True,
        conf=0.25,
        iou=0.45,
        epochs=200,
        patience=20
    )

if __name__ == "__main__":
    main()
