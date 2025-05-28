
# Quick Start Guide

## 1. Set up dataset structure
python setup_datasets.py

## 2. Download pre-trained models
python train_models.py --download-datasets

## 3. Collect your data following the guide in dataset_collection_guide.md

## 4. Train models (example for nudity detection)
python train_models.py --category nudity --dataset_dir ./datasets/nudity --epochs 20

## 5. Test your trained models
python test_trained_models.py

## 6. Deploy the models
# Copy your trained models to the models/ directory
# Update the moderation service to use MLModerationService
