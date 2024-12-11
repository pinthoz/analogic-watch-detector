from ultralytics import YOLO
model = YOLO('yolov8s.pt')

results = model.tune(data='dataset.yaml', epochs=25,           
    iterations=10,           
    device=0,
    optimizer='adamw',
    plots=True,
    save=True,
    conf=0.25,
    iou=0.45)