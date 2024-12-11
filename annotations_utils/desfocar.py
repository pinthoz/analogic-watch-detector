import os
import cv2
import albumentations as A


def read_annotations(file_path):
    annotations = []
    with open(file_path, "r") as f:
        for line in f:
            annotations.append(line.strip())
    return annotations


images_folder = r"C:\Users\anoca\Documents\GitHub\analogic-watch-detector\rr"
labels_folder = r"C:\Users\anoca\Documents\GitHub\analogic-watch-detector"
output_images_folder = r"C:\Users\anoca\Documents\GitHub\analogic-watch-detector\rr"
output_labels_folder = r"C:\Users\anoca\Documents\GitHub\analogic-watch-detector"


os.makedirs(output_images_folder, exist_ok=True)
os.makedirs(output_labels_folder, exist_ok=True)


transform = A.Compose([
    A.Blur(blur_limit=43, p=1.0)  
])


for image_filename in os.listdir(images_folder):
   
    if "rotated" in image_filename or "zoom_out" in image_filename:
        print(f"Ignorado: {image_filename} (contém 'rotated' ou 'zoom_out')")
        continue

    
    if image_filename.endswith((".jpg", ".png", ".jpeg")):
        image_path = os.path.join(images_folder, image_filename)
        label_path = os.path.join(labels_folder, image_filename.replace(".jpg", ".txt").replace(".png", ".txt").replace(".jpeg", ".txt"))

        
        if not os.path.exists(label_path):
            print(f"Anotação não encontrada para {image_filename}, pulando.")
            continue

        
        imagem = cv2.imread(image_path)

        
        imagem_desfocada = transform(image=imagem)['image']

        
        base_name, ext = os.path.splitext(image_filename)  
        new_image_name = f"{base_name}_blurred{ext}"
        new_label_name = f"{base_name}_blurred.txt"

       
        output_image_path = os.path.join(output_images_folder, new_image_name)
        cv2.imwrite(output_image_path, imagem_desfocada)

        
        new_label_path = os.path.join(output_labels_folder, new_label_name)
        annotations = read_annotations(label_path)
        with open(new_label_path, "w") as f:
            for line in annotations:
                f.write(line + "\n")

        print(f"Imagem processada e salva como: {new_image_name}")
        print(f"Anotações copiadas e salvas como: {new_label_name}")
