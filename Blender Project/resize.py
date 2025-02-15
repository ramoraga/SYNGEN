import os
from PIL import Image, ImageOps
import pillow_heif  # Import the HEIC support library

def resize(input_folder, output_folder, target_size=(640, 640)):
    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)

    count = 67
    for filename in sorted(os.listdir(input_folder)):
        input_path = os.path.join(input_folder, filename)
        output_name = f"test_{count:03d}.png"  # Rename pattern
        output_path = os.path.join(output_folder, output_name)

        try:
            # Open the image (HEIC is supported via pillow-heif)
            with Image.open(input_path) as img:
                # Convert the image to RGB if necessary (e.g., HEIC)
                img = img.convert("RGB")
                
                # Resize the image while preserving aspect ratio
                img = ImageOps.fit(img, target_size, method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))
                
                # Save the resized image as PNG
                img.save(output_path, format="PNG")
                print(f"Resized, converted, and saved: {output_path}")
                count += 1
        except Exception as e:
            print(f"Skipping file {filename}: {e}")

# Example usage
input_folder = "/home/rmoraga/CAD Project/Prismatic Geometries/test_dataset/raw"
output_folder = "/home/rmoraga/CAD Project/Prismatic Geometries/test_dataset"
resize(input_folder, output_folder)
