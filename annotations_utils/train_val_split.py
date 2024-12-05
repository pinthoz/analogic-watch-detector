import os
import shutil
from sklearn.model_selection import train_test_split

def split_dataset(images_dir, labels_dir, val_images_dir, val_labels_dir, val_ratio=0.2):
    """
    Divide o conjunto de dados em treino e validação, excluindo imagens "_rotated".
    
    :param images_dir: Diretório das imagens originais.
    :param labels_dir: Diretório das labels originais.
    :param val_images_dir: Diretório para salvar imagens de validação.
    :param val_labels_dir: Diretório para salvar labels de validação.
    :param val_ratio: Proporção de imagens a serem usadas na validação.
    """
    # Cria pastas de validação, se não existirem
    os.makedirs(val_images_dir, exist_ok=True)
    os.makedirs(val_labels_dir, exist_ok=True)

    # Lista de imagens normais (sem _rotated)
    normal_images = [f for f in os.listdir(images_dir) if f.endswith(".jpg") and "_rotated" not in f]
    
    # Associa labels existentes
    normal_images = [f for f in normal_images if os.path.exists(os.path.join(labels_dir, f.replace(".jpg", ".txt")))]
    
    # Divide em treino e validação
    train_images, val_images = train_test_split(normal_images, test_size=val_ratio, random_state=42)
    
    # Move as imagens e labels para o diretório de validação
    for image in val_images:
        label = image.replace(".jpg", ".txt")
        
        # Move a imagem
        shutil.move(os.path.join(images_dir, image), os.path.join(val_images_dir, image))
        
        # Move a label
        shutil.move(os.path.join(labels_dir, label), os.path.join(val_labels_dir, label))

    print(f"Divisão concluída! {len(val_images)} imagens movidas para validação.")

# Exemplos de uso
split_dataset(
    images_dir="dataset/images/train",
    labels_dir="dataset/labels/train",
    val_images_dir="dataset/images/val",
    val_labels_dir="dataset/labels/val",
    val_ratio=0.2
)
