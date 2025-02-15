import os
import cv2
import numpy as np

def generate_yolo_labels(rgb_dir, mask_dir, label_dir, class_map):
    os.makedirs(label_dir, exist_ok=True)

    rgb_files = sorted([f for f in os.listdir(rgb_dir) if f.endswith('.png') or f.endswith('.jpg')])
    mask_files = sorted([f for f in os.listdir(mask_dir) if f.endswith('.png') or f.endswith('.jpg')])

    for rgb_file, mask_file in zip(rgb_files, mask_files):
        rgb_path = os.path.join(rgb_dir, rgb_file)
        mask_path = os.path.join(mask_dir, mask_file)

        # Determine class from the file name
        class_name = rgb_file.split('_')[0]  # Assumes format "class_name_*"
        class_id = class_map.get(class_name, -1)

        if class_id == -1:
            print(f"Unknown class name '{class_name}' in file '{rgb_file}'. Skipping.")
            continue

        # Load mask image
        mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
        if mask is None:
            print(f"Could not read mask: {mask_path}")
            continue

        # Threshold to ensure binary mask
        _, binary_mask = cv2.threshold(mask, 127, 255, cv2.THRESH_BINARY)

        # Find contours in the binary mask
        contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Get image dimensions
        height, width = mask.shape

        # Prepare label file content
        label_content = []
        for contour in contours:
            # Normalize contour points
            normalized_points = []
            for point in contour:
                x, y = point[0]  # Extract x, y from the point array
                normalized_x = x / width
                normalized_y = y / height
                normalized_points.extend([normalized_x, normalized_y])

            # Convert normalized points to YOLO polygon format
            if len(normalized_points) >= 6:  # Ensure the polygon has at least 3 points
                points_str = " ".join(f"{p:.6f}" for p in normalized_points)
                label_content.append(f"{class_id} {points_str}")

        # Save label file
        label_file = os.path.join(label_dir, os.path.splitext(rgb_file)[0] + ".txt")
        with open(label_file, 'w') as file:
            file.write("\n".join(label_content))

        print(f"Label file created: {label_file}")

if __name__ == "__main__":
    # Directories
    rgb_directory = "/home/rmoraga/CAD Project/Prismatic Geometries/quantity_dataset/val/images"
    mask_directory = "/home/rmoraga/CAD Project/Prismatic Geometries/quantity_dataset/val/masks"
    label_directory = "/home/rmoraga/CAD Project/Prismatic Geometries/quantity_dataset/val/labels"
    
    # Class mapping
    class_mapping = {
        "bolt": 0,
        "tshape": 1,
        "yoke": 2,
        "null": 3
    }

    # Generate labels
    generate_yolo_labels(rgb_directory, mask_directory, label_directory, class_mapping)
