import os
import cv2
import albumentations as A

# Função para ajustar as anotações após transformação
def adjust_annotations(annotations, original_size, resized_size, padded_size):
    orig_h, orig_w = original_size
    resized_h, resized_w = resized_size
    padded_h, padded_w = padded_size

    scale_x = resized_w / orig_w  # Escala para largura
    scale_y = resized_h / orig_h  # Escala para altura

    pad_x = (padded_w - resized_w) / 2  # Padding horizontal
    pad_y = (padded_h - resized_h) / 2  # Padding vertical

    adjusted_annotations = []
    for ann in annotations:
        cls, x_c, y_c, w, h = ann

        # Ajustar coordenadas normalizadas para o redimensionamento
        x_c = x_c * orig_w * scale_x
        y_c = y_c * orig_h * scale_y
        w = w * orig_w * scale_x
        h = h * orig_h * scale_y

        # Ajustar para o padding e normalizar para o novo tamanho
        x_c = (x_c + pad_x) / padded_w
        y_c = (y_c + pad_y) / padded_h
        w = w / padded_w
        h = h / padded_h

        # Adicionar anotação ajustada
        adjusted_annotations.append((cls, x_c, y_c, w, h))
    
    return adjusted_annotations

# Função para ler as anotações de um arquivo
def read_annotations(file_path):
    annotations = []
    with open(file_path, "r") as f:
        for line in f:
            parts = line.strip().split()
            cls = int(parts[0])  # Classe
            x_c, y_c, w, h = map(float, parts[1:])
            annotations.append((cls, x_c, y_c, w, h))
    return annotations

# Configuração de transformações
resize_height, resize_width = 128, 128
padded_height, padded_width = 256, 256
augmentation = A.Compose([
    A.Resize(height=resize_height, width=resize_width),
    A.PadIfNeeded(min_height=padded_height, min_width=padded_width, border_mode=cv2.BORDER_CONSTANT, value=(0, 0, 0)),
])

# Caminhos das pastas
images_folder = r"C:\Users\anoca\Documents\GitHub\analogic-watch-detector\dataset\images\train"
labels_folder = r"C:\Users\anoca\Documents\GitHub\analogic-watch-detector\dataset\labels\train"
output_images_folder = r"C:\Users\anoca\Documents\GitHub\analogic-watch-detector\dataset\images\train"
output_labels_folder = r"C:\Users\anoca\Documents\GitHub\analogic-watch-detector\dataset\labels\train"

# Certificar-se de que as pastas de saída existem
os.makedirs(output_images_folder, exist_ok=True)
os.makedirs(output_labels_folder, exist_ok=True)

# Processar todos os arquivos na pasta
for image_filename in os.listdir(images_folder):
    # Pular arquivos com "rotated" no nome
    if "rotated" in image_filename:
        print(f"Pulado: {image_filename} (contém 'rotated').")
        continue

    if image_filename.endswith((".jpg", ".png", ".jpeg")):  # Verifica formatos de imagem
        image_path = os.path.join(images_folder, image_filename)
        label_path = os.path.join(labels_folder, image_filename.replace(".jpg", ".txt").replace(".png", ".txt").replace(".jpeg", ".txt"))

        # Verificar se o arquivo de anotações correspondente existe
        if not os.path.exists(label_path):
            print(f"Anotação não encontrada para {image_filename}, pulando.")
            continue

        # Carregar a imagem e as anotações
        image = cv2.imread(image_path)
        original_size = image.shape[:2]  # (altura, largura)
        annotations = read_annotations(label_path)

        # Aplicar transformações
        augmented = augmentation(image=image)
        augmented_image = augmented["image"]

        # Ajustar as anotações
        new_annotations = adjust_annotations(
            annotations,
            original_size=(original_size[0], original_size[1]),
            resized_size=(resize_height, resize_width),
            padded_size=(padded_height, padded_width)
        )

        # Criar novo nome para a imagem e as anotações
        base_name, ext = os.path.splitext(image_filename)
        new_image_name = f"{base_name}_zoom_out{ext}"
        new_label_name = f"{base_name}_zoom_out.txt"

        # Salvar imagem transformada
        output_image_path = os.path.join(output_images_folder, new_image_name)
        cv2.imwrite(output_image_path, augmented_image)

        # Salvar anotações transformadas
        output_label_path = os.path.join(output_labels_folder, new_label_name)
        with open(output_label_path, "w") as f:
            for ann in new_annotations:
                f.write(f"{ann[0]} {ann[1]:.6f} {ann[2]:.6f} {ann[3]:.6f} {ann[4]:.6f}\n")

        print(f"Processado e salvo como: {new_image_name}")
