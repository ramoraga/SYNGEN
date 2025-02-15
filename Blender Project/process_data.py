import OpenEXR
import Imath
import numpy as np
import cv2
import os
import shutil

def save_masks(input_folder, output_folder, prefix="rgb"):
    # Create output directory if it doesn’t exist
    os.makedirs(output_folder, exist_ok=True)
    
    # Initialize the counter
    index = 1

    # Iterate through PNG files in the input folder
    for filename in sorted(os.listdir(input_folder)):
        if filename.endswith(".png"):
            # Define the new filename with zero-padded numbering
            new_filename = f"null_{prefix}_{index:03d}.png"
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, new_filename)
            
            # Copy the file to the output folder with the new name
            shutil.copy(input_path, output_path)
            print(f"Renamed {filename} to {new_filename}")
            
            # Increment the index for the next file
            index += 1

def extract_rgbd(input_folder, output_rgb_folder, output_depth_folder):
    # Create output directories if they don’t exist
    os.makedirs(output_rgb_folder, exist_ok=True)
    os.makedirs(output_depth_folder, exist_ok=True)
    
    # Initialize the counter
    index = 1
    
    # Loop over all EXR files in the input folder
    for filename in sorted(os.listdir(input_folder)):
        if filename.endswith(".exr"):
            exr_path = os.path.join(input_folder, filename)
            
            # Open the EXR file
            exr_file = OpenEXR.InputFile(exr_path)
            header = exr_file.header()
            
            # Define the data window to read the entire image
            dw = header['dataWindow']
            width, height = dw.max.x - dw.min.x + 1, dw.max.y - dw.min.y + 1

            # Extract RGB channels with updated channel names
            rgb_channels = ["RGB.R", "RGB.G", "RGB.B"]
            rgb_data = [np.frombuffer(exr_file.channel(c, Imath.PixelType(Imath.PixelType.FLOAT)), dtype=np.float32) for c in rgb_channels]
            rgb_data = np.stack(rgb_data, axis=-1).reshape((height, width, 3))
            
            # Normalize RGB to 0-255 and save as PNG
            rgb_data = np.clip(rgb_data * 255.0, 0, 255).astype(np.uint8)
            rgb_output_path = os.path.join(output_rgb_folder, f"null_rgb_{index:03d}.png")
            cv2.imwrite(rgb_output_path, cv2.cvtColor(rgb_data, cv2.COLOR_RGB2BGR))
            
            # Extract Depth channel with the correct channel name
            depth_data = np.frombuffer(exr_file.channel("Depth.V", Imath.PixelType(Imath.PixelType.FLOAT)), dtype=np.float32)
            depth_data = depth_data.reshape((height, width))

            # Optional: Normalize depth data (scale to 0-255) for visualization or storage
            depth_data = np.clip((depth_data - np.min(depth_data)) / (np.max(depth_data) - np.min(depth_data)) * 255, 0, 255).astype(np.uint8)

            # Invert the depth image
            depth_data = 255 - depth_data

            # Save the inverted depth image
            depth_output_path = os.path.join(output_depth_folder, f"null_depth_{index:03d}.png")
            cv2.imwrite(depth_output_path, depth_data)
            
            print(f"Processed {filename}: Saved RGB to {rgb_output_path} and Depth to {depth_output_path}")
            
            # Increment the index for the next file
            index += 1

# Example usage
home = "/home/rmoraga/CAD Project/Prismatic Geometries"

input_exr = f"{home}/raw/train/images"
input_masks = f"{home}/real_dataset"
output_rgb = f"{home}/dataset_v2/train/rgb"
output_depth = f"{home}/dataset_v2/train/depth"
output_masks = f"{home}/real_dataset/images"

os.makedirs("output", exist_ok=True)
#extract_rgbd(input_exr, output_rgb, output_depth)
save_masks(input_masks, output_masks)

