import cv2
from ultralytics import YOLO  # Importa a biblioteca YOLO (ajuste conforme o framework usado)

# Carrega o modelo treinado
model = YOLO(r'C:\Users\anoca\Documents\GitHub\analogic-watch-detector\runs\detect\train44\weights\best.pt')  # Substitua pelo caminho correto do seu modelo

# Configura a captura de vídeo (0 geralmente é a câmera padrão)
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Erro ao acessar a câmera")
    exit()

while True:
    # Captura frame por frame
    ret, frame = cap.read()
    if not ret:
        print("Não foi possível capturar o frame. Encerrando...")
        break

    # Realiza a detecção no frame capturado
    results = model(frame)

    # Desenha as detecções no frame
    annotated_frame = results[0].plot()

    # Exibe o frame processado
    cv2.imshow("Detecção YOLO", annotated_frame)

    # Sai ao pressionar 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Libera os recursos da câmera e fecha as janelas
cap.release()
cv2.destroyAllWindows()
