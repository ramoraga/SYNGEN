import os
import cv2
from ultralytics import YOLO
from pathlib import Path

def perform_inference(input_folder, output_folder, model_path, conf_threshold=0.25):
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Load the YOLO model
    model = YOLO(model_path)

    # Process each image in the input folder
    for image_file in os.listdir(input_folder):
        input_path = os.path.join(input_folder, image_file)
        
        # Ensure it's an image file
        if not image_file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
            print(f"Skipping non-image file: {image_file}")
            continue

        # Perform inference
        results = model(input_path, conf=conf_threshold)
        
        # Get the annotated image
        annotated_frame = results[0].plot()

        # Save the annotated image to the output folder
        output_path = os.path.join(output_folder, image_file)
        cv2.imwrite(output_path, annotated_frame)
        print(f"Processed and saved: {output_path}")

    print("Inference completed.")

# Example usage
if __name__ == "__main__":
    # Define paths
    input_folder = "/home/rmoraga/CAD Project/Prismatic Geometries/test_dataset"  # Folder with input images
    output_folder = "/home/rmoraga/YOLO Training/runs/segment/quantity/test"  # Folder to save output images
    model_path = "/home/rmoraga/YOLO Training/runs/segment/quantity/weights/best.pt"  # Path to your YOLOv8 model

    # Perform inference
    perform_inference(input_folder, output_folder, model_path)
