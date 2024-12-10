import cv2
from ultralytics import YOLO


model = YOLO(r'C:\Users\anoca\Documents\GitHub\analogic-watch-detector\runs\detect\train44\weights\best.pt') 


cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error accessing the camera. Exiting...")
    exit()

while True:
    # Capturing a frame
    ret, frame = cap.read()
    if not ret:
        print("Não foi possível capturar o frame. Encerrando...")
        break

    # Executing the model in the frame
    results = model(frame)

    # Annotating the frame with the detections
    annotated_frame = results[0].plot()

    # Displaying the frame
    cv2.imshow("Detecção YOLO", annotated_frame)

    # Press 'esc' to exit
    if cv2.waitKey(1) & 0xFF == ord('esc'):
        break


cap.release()
cv2.destroyAllWindows()
