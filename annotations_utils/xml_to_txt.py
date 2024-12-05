import os
import xml.etree.ElementTree as ET

# Mapeamento das classes
class_mapping = {
    "circle": 0,
    "hours": 1,
    "minutes": 2,
    "seconds": 3,
    "12": 4
}

# Diretório contendo os arquivos XML
input_dir = r"C:\Users\anoca\Documents\GitHub\analogic-watch-detector\dataset\images\train"

def convert_xml_to_yolo(xml_file, output_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    image_width = int(root.find('size/width').text)
    image_height = int(root.find('size/height').text)
    
    yolo_annotations = []

    for obj in root.findall('object'):
        class_name = obj.find('name').text
        class_id = class_mapping[class_name]

        xmin = int(obj.find('bndbox/xmin').text)
        ymin = int(obj.find('bndbox/ymin').text)
        xmax = int(obj.find('bndbox/xmax').text)
        ymax = int(obj.find('bndbox/ymax').text)

        x_center = ((xmin + xmax) / 2) / image_width
        y_center = ((ymin + ymax) / 2) / image_height
        width = (xmax - xmin) / image_width
        height = (ymax - ymin) / image_height

        yolo_annotations.append(f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}")

    with open(output_file, 'w') as f:
        f.write("\n".join(yolo_annotations))

# Processar todos os arquivos XML no diretório
for filename in os.listdir(input_dir):
    if filename.endswith(".xml"):
        xml_path = os.path.join(input_dir, filename)
        txt_filename = os.path.splitext(filename)[0] + ".txt"
        txt_path = os.path.join(input_dir, txt_filename)
        
        try:
            convert_xml_to_yolo(xml_path, txt_path)
            print(f"Convertido: {xml_path} -> {txt_path}")
            
            # Apagar o arquivo XML após a conversão
            os.remove(xml_path)
            print(f"Arquivo XML apagado: {xml_path}")
        except Exception as e:
            print(f"Erro ao processar {xml_path}: {e}")
