# Leveraging Synthetic Data for Efficient Training of AI Models for Real-World Object Detection

This repository contains the implementation and resources for my thesis research, which explores the effectiveness of using synthetic data to train computer vision models for real-world object detection. The project leverages Blender for synthetic image generation and Detectron2 and YOLOv8 for model training and evaluation. **SYNGEN** or Syntehtic Data Generator is the script that was developed in conjunction with Blender to generate images of the 3D virtual environment.

**Project Overview**

Traditional computer vision models require large, high-quality, and well-annotated real-world datasets, which can be expensive and time-consuming to collect. This project investigates an alternative approach: using synthetic images generated from 3D CAD models to train AI-driven object detection models while maintaining performance comparable to real-world datasets.

**Pipeline**

The core of this research revolves around an automated synthetic data generation pipeline that consists of:
1. **Blender-based Image Rendering** – A custom Blender script generates a structured dataset with RGB, depth, and segmentation mask images.
2. **Data Processing & Annotation** – Using OpenCV and OpenEXR, the generated images are structured into COCO-format datasets.
3. **Neural Network Training** – Two state-of-the-art AI-CV architectures, Detectron2 (Mask R-CNN, Faster R-CNN) and YOLOv8, are trained on the synthetic dataset.
4. **Performance Evaluation** – Models trained on synthetic data are validated using real-world images to assess generalization capability.

**Key Findings**

- Synthetic data can achieve comparable performance to real-world data for object detection tasks.
- Domain randomization and dataset augmentation significantly impact model accuracy.
- Certain object geometries and occlusion conditions affect the synthetic-to-real transferability of trained models.
