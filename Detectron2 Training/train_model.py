from detectron2.data import DatasetCatalog, MetadataCatalog
from detectron2.structures import BoxMode
from detectron2.engine import DefaultTrainer, hooks
from detectron2.evaluation import COCOEvaluator
from detectron2.engine import DefaultTrainer
from detectron2.config import get_cfg
from detectron2 import model_zoo
import os
import json


def load_custom_dataset(json_path, image_dir):
    with open(json_path) as f:
        coco_dict = json.load(f)
    dataset_dicts = []
    for img in coco_dict["images"]:
        record = {}
        record["file_name"] = os.path.join(image_dir, img["file_name"])
        record["image_id"] = img["id"]
        record["height"] = img["height"]
        record["width"] = img["width"]
        
        annotations = [ann for ann in coco_dict["annotations"] if ann["image_id"] == img["id"]]
        objs = []
        for ann in annotations:
            obj = {
                "bbox": ann["bbox"],
                "bbox_mode": BoxMode.XYWH_ABS,
                "segmentation": ann["segmentation"],
                "category_id": ann["category_id"]
            }
            objs.append(obj)
        record["annotations"] = objs
        dataset_dicts.append(record)
    return dataset_dicts

# Register the training dataset
DatasetCatalog.register("my_dataset", lambda: load_custom_dataset("quantity_train.json", "/home/rmoraga/CAD Project/Prismatic Geometries/quantity_dataset/train/images"))
MetadataCatalog.get("my_dataset").set(thing_classes=["bolt", "tshape", "yoke"])

# Register validation dataset
DatasetCatalog.register("my_validation_dataset", lambda: load_custom_dataset("quantity_val.json", "/home/rmoraga/CAD Project/Prismatic Geometries/quantity_dataset/val/images"))
MetadataCatalog.get("my_validation_dataset").set(thing_classes=["bolt", "tshape", "yoke"])

adv_model = model_zoo.get_config_file("COCO-InstanceSegmentation/mask_rcnn_X_101_32x8d_FPN_3x.yaml")
reg_model = model_zoo.get_config_file("COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml")

cfg = get_cfg()
cfg.merge_from_file(reg_model)
cfg.DATASETS.TRAIN = ("my_dataset",)  # Training dataset
cfg.DATASETS.TEST = ("my_validation_dataset",)  # Validation dataset
cfg.DATALOADER.NUM_WORKERS = 2
cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url("COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml")
cfg.SOLVER.IMS_PER_BATCH = 8
cfg.SOLVER.BASE_LR = 0.0001
cfg.SOLVER.WEIGHT_DECAY = 0.0001
cfg.SOLVER.MAX_ITER = 3000
cfg.TEST.EVAL_PERIOD = 500  # Evaluate on the validation set every 1000 iterations
cfg.MODEL.ROI_HEADS.NUM_CLASSES = 3  # Update with the number of classes in your dataset

# Define the trainer with evaluation hooks
class TrainerWithValidation(DefaultTrainer):
    @classmethod
    def build_evaluator(cls, cfg, dataset_name):
        return COCOEvaluator(dataset_name, cfg, False, output_dir="./output/")

# Create the output directory
os.makedirs(cfg.OUTPUT_DIR, exist_ok=True)

# Train with validation
trainer = TrainerWithValidation(cfg)
trainer.resume_or_load(resume=False)

# Add evaluation hooks
trainer.register_hooks([hooks.EvalHook(0, lambda: trainer.test(cfg, trainer.model))])

# Start training
trainer.train()
