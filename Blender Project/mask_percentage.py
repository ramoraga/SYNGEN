import cv2
import numpy as np
import os

def process_masks(input_folder, output_folder, object_name):
    # Ensure output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Get all image files in the input folder
    image_files = [f for f in os.listdir(input_folder) if f.endswith(('.png', '.jpg', '.jpeg'))]

    for i, filename in enumerate(image_files):
        image_path = os.path.join(input_folder, filename)

        # Load the image in grayscale mode
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

        # Convert to binary (thresholding)
        _, binary_image = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY)

        # Count white (mask) and total pixels
        white_pixels = np.count_nonzero(binary_image == 255)
        total_pixels = binary_image.size

        # Calculate percentage
        mask_percentage = (white_pixels / total_pixels) * 100

        # Format new filename
        new_filename = f"{object_name}_{i:04d}_{mask_percentage:.2f}.png"
        new_image_path = os.path.join(output_folder, new_filename)

        # Save the binary image with new filename
        cv2.imwrite(new_image_path, binary_image)
        print(f"Processed: {filename} -> {new_filename}")

# Example usage
input_folder = "/home/rmoraga/CAD Project/Prismatic Geometries/synthetic_dataset/train/masks"  # Change this to your input folder path
output_folder = "/home/rmoraga/CAD Project/test"  # Change this to your output folder path
object_name = "bolt"  # Change this to your object name

process_masks(input_folder, output_folder, object_name)
