#!/usr/bin/env python3
"""
Training script for image moderation models

This script shows how to:
1. Download and organize datasets
2. Train models for each category
3. Evaluate model performance
4. Save trained models

Usage:
    python train_models.py --category nudity --dataset_dir ./datasets/nudity
    python train_models.py --category drugs --dataset_dir ./datasets/drugs
    python train_models.py --category weapons --dataset_dir ./datasets/weapons
    python train_models.py --category hate_symbols --dataset_dir ./datasets/hate_symbols
"""

import argparse
import os
import sys
import logging
from typing import Tuple
import matplotlib.pyplot as plt

# Add app directory to path
sys.path.append('app')

from app.ml_moderation import ModelTrainer, DataCollector

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def download_datasets():
    """
    Download available datasets and models
    """
    print("📊 DATASET COLLECTION GUIDE")
    print("=" * 50)
    
    print("\n1. NUDITY DETECTION:")
    print("   • Download NSFW datasets from:")
    print("     - https://github.com/alex000kim/nsfw_data_scraper")
    print("     - https://github.com/GantMan/nsfw_model (pre-trained model)")
    print("     - Yahoo's Open NSFW dataset")
    print("   • Or use NudeNet pre-trained model")
    
    print("\n2. DRUG DETECTION:")
    print("   • Collect images of:")
    print("     - Pills/medications (from medical databases)")
    print("     - Drug paraphernalia (pipes, syringes)")
    print("     - White powder substances")
    print("     - Cannabis plants/products")
    print("   • Sources:")
    print("     - Medical image databases")
    print("     - Law enforcement training datasets")
    print("     - Google Images (with proper labeling)")
    
    print("\n3. WEAPON DETECTION:")
    print("   • Use COCO dataset filtered for weapons")
    print("   • Add custom weapon images:")
    print("     - Guns, knives, explosives")
    print("     - Military equipment")
    print("   • Sources:")
    print("     - COCO dataset")
    print("     - Open Images dataset")
    print("     - Security camera datasets")
    
    print("\n4. HATE SYMBOL DETECTION:")
    print("   • ADL Hate Symbols Database")
    print("   • Historical symbol collections")
    print("   • Text-based hate content")
    print("   • Custom symbol generation")
    
    # Download available pre-trained models
    DataCollector.download_pretrained_models()

def prepare_dataset_structure(category: str, dataset_dir: str):
    """
    Create proper dataset structure for training
    """
    print(f"\n📁 Setting up dataset structure for {category}")
    
    # Create directories
    train_dir = os.path.join(dataset_dir, "train")
    val_dir = os.path.join(dataset_dir, "validation")
    
    for split in [train_dir, val_dir]:
        positive_dir = os.path.join(split, "positive")
        negative_dir = os.path.join(split, "negative")
        
        os.makedirs(positive_dir, exist_ok=True)
        os.makedirs(negative_dir, exist_ok=True)
    
    print(f"✅ Dataset structure created:")
    print(f"   {train_dir}/positive/     <- Put {category} images here")
    print(f"   {train_dir}/negative/     <- Put safe images here")
    print(f"   {val_dir}/positive/       <- Put validation {category} images here")
    print(f"   {val_dir}/negative/       <- Put validation safe images here")
    
    return train_dir, val_dir

def train_category_model(category: str, dataset_dir: str, epochs: int = 20):
    """
    Train a model for a specific category
    """
    print(f"\n🚀 Training {category} detection model")
    print("=" * 50)
    
    # Initialize trainer
    trainer = ModelTrainer(category)
    
    # Prepare dataset structure
    train_dir, val_dir = prepare_dataset_structure(category, dataset_dir)
    
    # Check if datasets exist
    train_positive = os.path.join(train_dir, "positive")
    train_negative = os.path.join(train_dir, "negative")
    
    if not os.path.exists(train_positive) or not os.listdir(train_positive):
        print(f"❌ No training data found in {train_positive}")
        print(f"Please add {category} images to this directory")
        return None
    
    if not os.path.exists(train_negative) or not os.listdir(train_negative):
        print(f"❌ No negative training data found in {train_negative}")
        print("Please add safe images to this directory")
        return None
    
    try:
        # Prepare datasets
        print("📊 Preparing datasets...")
        train_dataset, val_dataset = trainer.prepare_dataset(train_dir)
        
        # Create model
        print("🏗️ Creating model architecture...")
        model = trainer.create_model(num_classes=2)
        
        print("📋 Model Summary:")
        model.summary()
        
        # Train model
        print(f"🔥 Training model for {epochs} epochs...")
        history = trainer.train_model(model, train_dataset, val_dataset, epochs)
        
        # Save model
        model_path = f"models/{category}_detection_model.h5"
        os.makedirs("models", exist_ok=True)
        trainer.save_model(model, model_path)
        
        # Plot training history
        plot_training_history(history, category)
        
        # Evaluate model
        evaluate_model(model, val_dataset, category)
        
        print(f"✅ {category} model training completed!")
        print(f"Model saved to: {model_path}")
        
        return model_path
        
    except Exception as e:
        print(f"❌ Error training {category} model: {e}")
        return None

def plot_training_history(history, category: str):
    """
    Plot training history
    """
    plt.figure(figsize=(12, 4))
    
    plt.subplot(1, 2, 1)
    plt.plot(history.history['accuracy'], label='Training Accuracy')
    plt.plot(history.history['val_accuracy'], label='Validation Accuracy')
    plt.title(f'{category} Model Accuracy')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy')
    plt.legend()
    
    plt.subplot(1, 2, 2)
    plt.plot(history.history['loss'], label='Training Loss')
    plt.plot(history.history['val_loss'], label='Validation Loss')
    plt.title(f'{category} Model Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()
    
    plt.tight_layout()
    plt.savefig(f'training_history_{category}.png')
    plt.show()

def evaluate_model(model, val_dataset, category: str):
    """
    Evaluate model performance
    """
    print(f"\n📊 Evaluating {category} model...")
    
    # Evaluate on validation set
    loss, accuracy = model.evaluate(val_dataset, verbose=0)
    
    print(f"Validation Loss: {loss:.4f}")
    print(f"Validation Accuracy: {accuracy:.4f}")
    
    # Calculate additional metrics if needed
    # (precision, recall, F1-score, etc.)

def create_sample_training_script():
    """
    Create a sample training script for reference
    """
    script_content = """
# Sample training workflow

# 1. Collect datasets for each category
python train_models.py --download-datasets

# 2. Organize your data according to the structure shown
# Add images to the appropriate directories

# 3. Train models for each category
python train_models.py --category nudity --dataset_dir ./datasets/nudity --epochs 20
python train_models.py --category drugs --dataset_dir ./datasets/drugs --epochs 20
python train_models.py --category weapons --dataset_dir ./datasets/weapons --epochs 20
python train_models.py --category hate_symbols --dataset_dir ./datasets/hate_symbols --epochs 20

# 4. Test the trained models
python test_trained_models.py
"""
    
    with open("training_workflow.txt", "w") as f:
        f.write(script_content)
    
    print("✅ Sample training workflow saved to training_workflow.txt")

def main():
    parser = argparse.ArgumentParser(description="Train image moderation models")
    parser.add_argument("--category", type=str, choices=["nudity", "drugs", "weapons", "hate_symbols"],
                        help="Category to train")
    parser.add_argument("--dataset_dir", type=str, help="Directory containing dataset")
    parser.add_argument("--epochs", type=int, default=20, help="Number of training epochs")
    parser.add_argument("--download-datasets", action="store_true", help="Download available datasets")
    parser.add_argument("--create-sample", action="store_true", help="Create sample training script")
    
    args = parser.parse_args()
    
    if args.download_datasets:
        download_datasets()
        return
    
    if args.create_sample:
        create_sample_training_script()
        return
    
    if not args.category or not args.dataset_dir:
        print("❌ Please specify --category and --dataset_dir")
        print("Example: python train_models.py --category nudity --dataset_dir ./datasets/nudity")
        return
    
    # Train the specified category
    model_path = train_category_model(args.category, args.dataset_dir, args.epochs)
    
    if model_path:
        print(f"\n🎉 Training completed successfully!")
        print(f"Model saved to: {model_path}")
        print("\nNext steps:")
        print("1. Test the model with sample images")
        print("2. Integrate into the moderation service")
        print("3. Deploy and monitor performance")
    else:
        print("❌ Training failed. Please check your dataset and try again.")

if __name__ == "__main__":
    main() 