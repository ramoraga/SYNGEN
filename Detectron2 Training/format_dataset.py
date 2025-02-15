import os
import json
import cv2
import numpy as np
from PIL import Image
from datetime import date

def format(images_dir, masks_dir, output_json):
    # Initialize COCO JSON structure
    coco_data = {
        "info": {
            "description": "Generated COCO Dataset",
            "year": 2025,
            "version": "1.0",
            "contributor": "Reinaldo Moraga",
            "date_created": str(date.today())
        },
        "licenses": [],
        "images": [],
        "annotations": [],
        "categories": [
            {"id": 0, "name": "bolt", "supercategory": "none"},
            {"id": 1, "name": "tshape", "supercategory": "none"},
            {"id": 2, "name": "yoke", "supercategory": "none"},
            {"id": 3, "name": "null", "supercategory": "none"}
        ]
    }
    
    class_to_id = {"bolt": 0, "tshape": 1, "yoke": 2, "null": 3}
    annotation_id = 0
    image_id = 0

    # Loop through image files
    for image_file in os.listdir(images_dir):
        if image_file.endswith(".png"):
            # Extract components from filename
            parts = image_file.split('_')
            class_name = parts[0]
            file_id = parts[-1].split('.')[0]

            # Validate class name
            if class_name not in class_to_id:
                continue
            
            image_path = os.path.join(images_dir, image_file)
            mask_path = os.path.join(masks_dir, f"{class_name}_mask_{file_id}.png")
            
            # Check if corresponding mask exists
            if os.path.exists(mask_path):
                # Open image and get dimensions
                image = Image.open(image_path)
                width, height = image.size
                
                # Add image entry to COCO
                coco_data["images"].append({
                    "id": image_id,
                    "file_name": image_file,
                    "width": width,
                    "height": height
                })
                
                # Open mask and find contours
                mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
                _, binary_mask = cv2.threshold(mask, 1, 255, cv2.THRESH_BINARY)
                contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                for contour in contours:
                    # Calculate bounding box and segmentation
                    x, y, w, h = cv2.boundingRect(contour)
                    segmentation = [contour.flatten().tolist()]
                    area = cv2.contourArea(contour)
                    
                    # Add annotation
                    coco_data["annotations"].append({
                        "id": annotation_id,
                        "image_id": image_id,
                        "category_id": class_to_id[class_name],
                        "bbox": [x, y, w, h],
                        "area": area,
                        "segmentation": segmentation,
                        "iscrowd": 0
                    })
                    annotation_id += 1
            
                image_id += 1

    # Save to output JSON file
    with open(output_json, 'w') as f:
        json.dump(coco_data, f, indent=4)

# Specify the input directories and output file
images_dir = "/home/rmoraga/CAD Project/Prismatic Geometries/quantity_dataset/train/images"  # Replace with the path to your RGB images directory
masks_dir = "/home/rmoraga/CAD Project/Prismatic Geometries/quantity_dataset/train/masks"    # Replace with the path to your masks directory
output_json = "quantity_train.json"

# Create COCO annotations
format(images_dir, masks_dir, output_json)

print(f"COCO annotations saved to {output_json}")
