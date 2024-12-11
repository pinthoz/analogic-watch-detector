import os
import random
import math
from PIL import Image, ImageDraw

def rotate_point(point, center, angle_deg):
    """
    Rotaciona um ponto ao redor de um centro em um determinado ângulo.
    """
    angle_rad = math.radians(angle_deg)
    x, y = point[0] - center[0], point[1] - center[1]
    x_rotated = x * math.cos(angle_rad) - y * math.sin(angle_rad)
    y_rotated = x * math.sin(angle_rad) + y * math.cos(angle_rad)
    return (x_rotated + center[0], y_rotated + center[1])

def draw_bounding_boxes(image_path, annotations_path, output_path):
    """
    Desenha caixas delimitadoras em uma imagem com base nas anotações YOLO.
    """
    with Image.open(image_path) as img:
        draw = ImageDraw.Draw(img)
        img_width, img_height = img.size
        
        with open(annotations_path, 'r') as f:
            lines = f.readlines()
        
        for line in lines:
            parts = line.strip().split()
            class_id = parts[0]
            x_center = float(parts[1]) * img_width
            y_center = float(parts[2]) * img_height
            width = float(parts[3]) * img_width
            height = float(parts[4]) * img_height
            
            x_min = x_center - width / 2
            y_min = y_center - height / 2
            x_max = x_center + width / 2
            y_max = y_center + height / 2
            
            # Desenha o retângulo
            draw.rectangle([x_min, y_min, x_max, y_max], outline="red", width=2)
            draw.text((x_min, y_min - 10), f"Class {class_id}", fill="red")
        
        img.save(output_path)
        print(f"Imagem com bounding boxes salva: {output_path}")

def rotate_yolo_annotations(input_txt, output_txt, angle, original_width, original_height, rotated_width, rotated_height):
    """
    Rotaciona as anotações YOLO para um ângulo específico, considerando o tamanho da imagem rotacionada.
    """
    with open(input_txt, 'r') as f:
        lines = f.readlines()
    
    new_annotations = []
    
    for line in lines:
        parts = line.strip().split()
        class_id = parts[0]
        x_center = float(parts[1]) * original_width
        y_center = float(parts[2]) * original_height
        width = float(parts[3]) * original_width
        height = float(parts[4]) * original_height
        
        if angle == -90:
            new_x_center = original_height - y_center
            new_y_center = x_center
            new_width = height
            new_height = width
        elif angle == 180:
            new_x_center = original_width - x_center
            new_y_center = original_height - y_center
            new_width = width
            new_height = height
        elif angle == -270:
            new_x_center = y_center
            new_y_center = original_width - x_center
            new_width = height
            new_height = width
        
        # Normaliza os valores para a escala [0, 1]
        norm_x_center = new_x_center / rotated_width
        norm_y_center = new_y_center / rotated_height
        norm_width = new_width / rotated_width
        norm_height = new_height / rotated_height
        
        # Gera a nova anotação YOLO
        new_annotation = f"{class_id} {norm_x_center:.6f} {norm_y_center:.6f} {norm_width:.6f} {norm_height:.6f}\n"
        new_annotations.append(new_annotation)
    
    # Salva as novas anotações no arquivo de saída
    with open(output_txt, 'w') as f:
        f.writelines(new_annotations)

def rotate_images_and_annotations(input_dir, output_dir):
    """
    Rotaciona imagens e suas anotações correspondentes em todos os ângulos especificados.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    angles = [-90, 180, -270]
    
    for filename in os.listdir(input_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
            try:
                input_img_path = os.path.join(input_dir, filename)
                input_txt_path = os.path.splitext(input_img_path)[0] + '.txt'
                
                with Image.open(input_img_path) as img:
                    original_width, original_height = img.size
                    
                    for angle in angles:
                        rotated_img = img.rotate(angle, expand=True)
                        rotated_width, rotated_height = rotated_img.size
                        name, ext = os.path.splitext(filename)
                        rotated_filename = f"{name}_rotated_{angle}{ext}"
                        output_img_path = os.path.join(output_dir, rotated_filename)
                        rotated_img.save(output_img_path)
                        print(f"Imagem salva: {output_img_path}")
                        
                        if os.path.exists(input_txt_path):
                            rotated_txt_filename = f"{name}_rotated_{angle}.txt"
                            output_txt_path = os.path.join(output_dir, rotated_txt_filename)
                            rotate_yolo_annotations(
                                input_txt_path, 
                                output_txt_path, 
                                angle, 
                                original_width, 
                                original_height, 
                                rotated_width, 
                                rotated_height
                            )
                            print(f"Anotação salva: {output_txt_path}")
                # Desenha bounding boxes antes e depois
                #annotated_image_path = os.path.join(output_dir, f"{name}_original_with_boxes{ext}")
                #draw_bounding_boxes(input_img_path, input_txt_path, annotated_image_path)
                
                #annotated_rotated_path = os.path.join(output_dir, f"{name}_rotated_with_boxes{ext}")
                #draw_bounding_boxes(output_img_path, output_txt_path, annotated_rotated_path)
                                
            except Exception as e:
                print(f"Erro ao processar {filename}: {e}")


# Configurações
input_directory = r"C:\Users\anoca\Downloads\Nova pasta"
output_directory = r"C:\Users\anoca\Downloads\Nova pasta\rotated"
rotate_images_and_annotations(input_directory, output_directory)
