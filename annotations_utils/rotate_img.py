import os
import random
from PIL import Image

def rotate_images(input_dir, output_dir):
    """
    Roda apenas uma imagem do diretório para um ângulo aleatório, salva a nova e remove a antiga.

    Args:
        input_dir (str): Diretório onde estão as imagens originais.
        output_dir (str): Diretório onde será salva a imagem rotacionada.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Lista todos os arquivos no diretório de entrada
    for filename in os.listdir(input_dir):
        input_path = os.path.join(input_dir, filename)
        
        # Verifica se o arquivo é uma imagem
        if not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
            continue
        
        try:
            # Escolhe um ângulo aleatório
            ang = [90, 270, 45, 135, 180, 225, 315]
            random_angle = random.choice(ang)
            
            # Abrir a imagem
            with Image.open(input_path) as img:
                # Rotacionar a imagem
                rotated_img = img.rotate(random_angle, expand=True)
                
                # Gerar nome para a imagem rotacionada
                name, ext = os.path.splitext(filename)
                rotated_filename = f"{name}_rotated_{random_angle}{ext}"
                output_path = os.path.join(output_dir, rotated_filename)
                
                # Salvar imagem rotacionada
                rotated_img.save(output_path)
                print(f"Imagem salva: {output_path}")
            
            # Remover a imagem original após gerar a versão rotacionada
            os.remove(input_path)
            print(f"Imagem original removida: {input_path}")
            
        except Exception as e:
            print(f"Erro ao processar {filename}: {e}")

# Configurações
input_directory = r"C:\Users\anoca\Documents\GitHub\analogic-watch-detector\dataset\images\train\novos\rodados"  # Substitua pelo diretório das imagens originais
output_directory = r"C:\Users\anoca\Documents\GitHub\analogic-watch-detector\dataset\images\train\novos\rodados"  # Substitua pelo diretório de saída

# Executar o script
rotate_images(input_directory, output_directory)

