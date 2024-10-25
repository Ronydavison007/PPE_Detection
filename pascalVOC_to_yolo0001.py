import os
import xml.etree.ElementTree as et
import argparse

def normalize_bbox(width, height, data):
    box_width = data[2] - data[0]
    box_height = data[3] - data[1]

    x_center = (data[0] + data[2]) / 2
    y_center = (data[1] + data[3]) / 2

    x_norm = x_center / width
    y_norm = y_center / height
    box_width_norm = box_width / width
    box_height_norm = box_height / height

    return x_norm, y_norm, box_width_norm, box_height_norm

def extract_annotations(xml_file, output_dir, class_map):
    print(f"Processing file: {xml_file}")
    tree = et.parse(xml_file)
    root = tree.getroot()

    size = root.find('size')
    width = int(size.find('width').text)
    height = int(size.find('height').text)

    output_file = os.path.join(output_dir, root.find('filename').text.replace('.jpg', '.txt').replace('.png', '.txt'))
    
    with open(output_file, 'w') as out:
        for obj in root.iter('object'):
            name = obj.find('name').text
            if name not in class_map:
                continue
            id = class_map[name]
            box = obj.find('bndbox')
            data = (
                float(box.find('xmin').text),
                float(box.find('ymin').text),
                float(box.find('xmax').text),
                float(box.find('ymax').text)
            )
            bb = normalize_bbox(width, height, data)
            out.write(f"{id} " + " ".join([f"{a:.6f}" for a in bb]) + '\n')

def xml_to_txt(xml_dir, output_dir, class_map):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for filename in os.listdir(xml_dir):
        if filename.endswith('.xml'):
            xml_file = os.path.join(xml_dir, filename)
            extract_annotations(xml_file, output_dir, class_map)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Converting data from PascalVOC to YoloV8 format")
    parser.add_argument('--xml_dir',type=str,required=True,help="Directory containing the PascalVOC format files")
    parser.add_argument('--output_dir',type=str,required=True,help="Directory containing the YoloV8 format files")
    parser.add_argument('--class_path', type=str, required=True, help='Path to the class mapping file')

    args = parser.parse_args()

    class_map = {}
    with open(args.class_path, 'r') as file:
        for id, line in enumerate(file):
            class_map[line.strip()] = id
    
    xml_to_txt(args.xml_dir, args.output_dir, class_map)

    print('Completed')
