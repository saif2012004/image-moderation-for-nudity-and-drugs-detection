#!/usr/bin/env python3
"""
Dataset setup script for image moderation training

This script helps you:
1. Download available pre-trained models
2. Set up dataset directories
3. Provide guidance on data collection
"""

import os
import urllib.request
import zipfile
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_dataset_structure():
    """Create the required dataset directory structure"""
    categories = ["nudity", "drugs", "weapons", "hate_symbols"]
    
    print("📁 Creating dataset directory structure...")
    
    for category in categories:
        for split in ["train", "validation"]:
            for label in ["positive", "negative"]:
                dir_path = f"datasets/{category}/{split}/{label}"
                os.makedirs(dir_path, exist_ok=True)
        
        print(f"✅ Created structure for {category}")
    
    print("\n📋 Dataset structure created:")
    print("datasets/")
    for category in categories:
        print(f"├── {category}/")
        print(f"│   ├── train/")
        print(f"│   │   ├── positive/     <- {category} images")
        print(f"│   │   └── negative/     <- safe images")
        print(f"│   └── validation/")
        print(f"│       ├── positive/     <- validation {category} images")
        print(f"│       └── negative/     <- validation safe images")

def download_pretrained_models():
    """Download available pre-trained models"""
    print("\n📥 Downloading pre-trained models...")
    
    os.makedirs("models", exist_ok=True)
    
    # List of available models to download
    models = {
        "nsfw_mobilenet": {
            "url": "https://github.com/GantMan/nsfw_model/releases/download/1.1.0/nsfw_mobilenet_v2_140_224.tflite",
            "description": "MobileNet v2 NSFW detection model"
        }
    }
    
    for model_name, info in models.items():
        try:
            filename = info["url"].split("/")[-1]
            filepath = f"models/{filename}"
            
            if not os.path.exists(filepath):
                print(f"Downloading {info['description']}...")
                urllib.request.urlretrieve(info["url"], filepath)
                print(f"✅ Downloaded {filename}")
            else:
                print(f"✅ {filename} already exists")
                
        except Exception as e:
            print(f"❌ Failed to download {model_name}: {e}")

def create_data_collection_guide():
    """Create a comprehensive data collection guide"""
    guide_content = """
# Image Moderation Dataset Collection Guide

## 1. NUDITY DETECTION

### Pre-trained Options:
- NudeNet: pip install nudenet
- NSFW Model: Available on GitHub (GantMan/nsfw_model)
- Yahoo Open NSFW: Classic model for NSFW detection

### Custom Dataset:
- **Positive samples (10,000+ images):**
  - Adult content (properly licensed)
  - Artistic nudity
  - Medical/anatomical images
  
- **Negative samples (10,000+ images):**
  - Regular photos of people (clothed)
  - Landscapes, objects
  - Animals, food, etc.

### Sources:
- SafeSearch disabled image searches
- Adult content platforms (with permission)
- Medical/educational databases
- Art museums collections

## 2. DRUG DETECTION

### Dataset Requirements:
- **Pills/Medications (3,000+ images):**
  - Various pill shapes, colors, sizes
  - Prescription bottles
  - Loose pills
  
- **Powders (2,000+ images):**
  - White powder substances
  - Various textures and containers
  
- **Paraphernalia (2,000+ images):**
  - Pipes, bongs, syringes
  - Rolling papers, scales
  - Drug preparation tools
  
- **Plants (2,000+ images):**
  - Cannabis plants and products
  - Other drug-related plants
  
- **Negative samples (10,000+ images):**
  - Regular household items
  - Food, spices, flour
  - Medical supplies (non-drug)

### Sources:
- Law enforcement training materials
- Medical databases
- Educational resources
- DEA image collections (public domain)

## 3. WEAPON DETECTION

### Dataset Requirements:
- **Guns (5,000+ images):**
  - Handguns, rifles, shotguns
  - Various angles and lighting
  - Real and toy weapons (labeled)
  
- **Knives (3,000+ images):**
  - Kitchen knives, tactical knives
  - Swords, machetes
  - Various blade types
  
- **Other weapons (2,000+ images):**
  - Clubs, brass knuckles
  - Explosives (training images)
  - Improvised weapons

### Sources:
- COCO dataset (filtered for weapons)
- Open Images dataset
- Military/police training datasets
- Security camera footage (anonymized)

## 4. HATE SYMBOL DETECTION

### Dataset Requirements:
- **Historical symbols (1,000+ images):**
  - Nazi symbols, KKK imagery
  - Various hate group logos
  
- **Modern hate symbols (1,000+ images):**
  - Online hate symbols
  - Coded imagery
  
- **Text-based hate (2,000+ images):**
  - Hate speech in images
  - Coded language
  
- **Negative samples (5,000+ images):**
  - Regular symbols, logos
  - Religious symbols
  - Cultural symbols

### Sources:
- ADL Hate Symbol Database
- Academic research collections
- News media archives
- Social media monitoring tools

## DATA COLLECTION BEST PRACTICES

### Legal Considerations:
1. Ensure you have proper licensing for all images
2. Respect copyright and privacy laws
3. Use public domain or creative commons when possible
4. Get permission for sensitive content

### Quality Guidelines:
1. High resolution images (minimum 224x224)
2. Various lighting conditions
3. Different angles and perspectives
4. Diverse backgrounds and contexts

### Labeling Standards:
1. Consistent naming convention
2. Clear positive/negative classification
3. Additional metadata when helpful
4. Quality control and verification

### Data Augmentation:
- Rotation, scaling, flipping
- Color adjustments
- Noise addition
- Cropping variations

## RECOMMENDED DATASET SIZES

| Category | Positive | Negative | Total |
|----------|----------|----------|-------|
| Nudity | 10,000+ | 10,000+ | 20,000+ |
| Drugs | 9,000+ | 10,000+ | 19,000+ |
| Weapons | 10,000+ | 10,000+ | 20,000+ |
| Hate Symbols | 4,000+ | 5,000+ | 9,000+ |

## TRAINING TIPS

1. **Start with pre-trained models** when available
2. **Use transfer learning** for faster training
3. **Validate thoroughly** with held-out test sets
4. **Monitor for bias** in your datasets
5. **Regular retraining** as new threats emerge
"""
    
    with open("dataset_collection_guide.md", "w", encoding="utf-8") as f:
        f.write(guide_content)
    
    print("✅ Data collection guide saved to 'dataset_collection_guide.md'")

def setup_quick_start():
    """Set up a quick start guide with example commands"""
    quick_start = """
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
"""
    
    with open("QUICK_START.md", "w") as f:
        f.write(quick_start)
    
    print("✅ Quick start guide saved to 'QUICK_START.md'")

def main():
    print("🚀 Setting up ML-based Image Moderation System")
    print("=" * 50)
    
    # Create dataset structure
    create_dataset_structure()
    
    # Download pre-trained models
    download_pretrained_models()
    
    # Create guides
    create_data_collection_guide()
    setup_quick_start()
    
    print("\n🎉 Setup completed!")
    print("\nNext steps:")
    print("1. Read 'dataset_collection_guide.md' for data collection")
    print("2. Follow 'QUICK_START.md' for training workflow")
    print("3. Collect and organize your training data")
    print("4. Train models using train_models.py")
    print("5. Integrate trained models into your API")
    
    print("\n📋 Available commands:")
    print("• python train_models.py --download-datasets")
    print("• python train_models.py --category nudity --dataset_dir ./datasets/nudity")
    print("• python train_models.py --category drugs --dataset_dir ./datasets/drugs")
    print("• python train_models.py --category weapons --dataset_dir ./datasets/weapons")
    print("• python train_models.py --category hate_symbols --dataset_dir ./datasets/hate_symbols")

if __name__ == "__main__":
    main() 