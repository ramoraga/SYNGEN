import cv2
import os
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from detectron2.utils.visualizer import Visualizer
from detectron2 import model_zoo
from detectron2.data import MetadataCatalog

# Load the trained model
cfg = get_cfg()
cfg.merge_from_file(model_zoo.get_config_file("COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml"))
cfg.MODEL.WEIGHTS = "output/quantity/model_final.pth"  # Path to your trained model
cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.5  # Confidence threshold
cfg.MODEL.ROI_HEADS.NUM_CLASSES = 3  # Adjust to the number of classes in your dataset
predictor = DefaultPredictor(cfg)

# Metadata (optional, for visualization purposes)
metadata = MetadataCatalog.get("my_dataset")  # Assuming "my_dataset" is registered with classes
MetadataCatalog.get("my_dataset").set(thing_classes=["bolt", "tshape", "yoke"])

# Define paths
input_dir = "/home/rmoraga/CAD Project/Prismatic Geometries/test_dataset"  # Folder containing input images
output_dir = "output/quantity/test"  # Folder to save output images
os.makedirs(output_dir, exist_ok=True)  # Ensure the output directory exists

# Perform inference on each image in the input folder
for file_name in os.listdir(input_dir):
    if file_name.lower().endswith(('.png', '.jpg', '.jpeg')):  # Ensure only image files are processed
        input_path = os.path.join(input_dir, file_name)
        output_path = os.path.join(output_dir, f"output_{file_name}")

        # Read the image
        image = cv2.imread(input_path)

        # Perform inference
        outputs = predictor(image)

        # Visualize the results (optional)
        v = Visualizer(image[:, :, ::-1], metadata, scale=1.2)
        out = v.draw_instance_predictions(outputs["instances"].to("cpu"))
        result_image = out.get_image()[:, :, ::-1]

        # Save the output image
        cv2.imwrite(output_path, result_image)

        print(f"Processed {file_name} -> {output_path}")
