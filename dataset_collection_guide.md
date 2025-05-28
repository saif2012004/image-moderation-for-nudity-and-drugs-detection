
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
