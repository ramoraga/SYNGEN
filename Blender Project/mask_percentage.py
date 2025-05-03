import cv2
import numpy as np
import os

''' The purpose of this script is to take an image mask and determine the percentage of foreground in the mask.
    This helps us determine how much of the occluded object of interest is actually being shown as a percentage,
    which helps us sort our occluded images and pick between a percentage range'''

def process_masks(input_folder, output_folder, object_name):
    # Ensure output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Get all image files in the masks folder
    image_files = [f for f in os.listdir(input_folder) if f.endswith(('.png', '.jpg', '.jpeg'))]

    for i, filename in enumerate(image_files):
        image_path = os.path.join(input_folder, filename)

        # Load the image in grayscale mode
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

        # Convert to binary (thresholding)
        _, binary_image = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY)

        # Count white (foreground) and total pixels
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

# Define paths
input_folder = "/home/rmoraga/CAD Project/Prismatic Geometries/synthetic_dataset/train/masks"  # Path to masks folder
output_folder = "/home/rmoraga/CAD Project/test"
object_name = "bolt"  # Change this to your object name

# Call function
process_masks(input_folder, output_folder, object_name)
