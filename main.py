import cv2
import math
from ultralytics import YOLO

# Funções para calcular o ângulo
def get_angle(p1, p2):
    angle = math.atan2(p1[1] - p2[1], p1[0] - p2[0])
    if angle < 0:
        angle += 2 * math.pi
    angle *= 180 / math.pi  # Para graus
    # Ajustar o ponto de 0 graus de direita para cima
    if angle <= 270:
        angle += 90
    else:
        angle -= 270
    return angle

def distance_between_points(p1, p2):
    return math.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)


# Carregue o modelo YOLO treinado
model = YOLO("clock_model.pt")  # Substitua pelo caminho do modelo treinado

# Carregue a imagem
image_path = "2.jpg"
src = cv2.imread(image_path)

if src is None:
    print("Nenhuma imagem carregada.")
    exit(-1)

# Realize a detecção com o modelo YOLO
results = model.predict(source=src, conf=0.5, save=False)

# Extraia as detecções
circle = None
hands = []
for result in results[0].boxes:
    cls = int(result.cls)  # Classe da detecção
    x1, y1, x2, y2 = map(int, result.xyxy[0])  # Coordenadas do retângulo

    if cls == 0:  # Círculo
        center = ((x1 + x2) // 2, (y1 + y2) // 2)
        radius = distance_between_points((x1, y1), (x2, y2)) // 2
        circle = (center, radius)
    else:  # Ponteiros
        hands.append(((x1 + x2) // 2, (y1 + y2) // 2, cls))  # cls identifica o tipo de ponteiro

# Desenhar os resultados
cdst = src.copy()
if circle:
    center, radius = circle
    cv2.circle(cdst, center, 3, (0, 255, 0), -1)
    cv2.circle(cdst, center, int(radius), (0, 0, 255), 3)

# Ordenar os ponteiros por comprimento
hands.sort(key=lambda h: distance_between_points(h[:2], center))

# Classificar os ponteiros e desenhar
colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]  # Azul: hora, Verde: minutos, Vermelho: segundos
labels = ["Hora", "Minutos", "Segundos"]
angles = []

for i, hand in enumerate(hands):
    hand_pos, cls = hand[:2], hand[2]
    cv2.line(cdst, center, hand_pos, colors[i], 3)
    angle = get_angle(hand_pos, center)
    angles.append(angle)
    print(f"{labels[i]}: {angle // (30 if i == 0 else 6)}")

# Exibir resultados
cv2.imshow("Fonte", src)
cv2.imshow("Detecção", cdst)
cv2.waitKey(0)
cv2.imwrite("detected_output.jpg", cdst)
cv2.destroyAllWindows()
