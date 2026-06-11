#!/usr/bin/env python3
"""
YOLO Dataset Preparation for Medical Waste Classification
Prepares training and validation datasets for three waste categories
"""

import os
import json
import shutil
import argparse
from pathlib import Path
import numpy as np
from datetime import datetime

class WasteDatasetPreparer:
    """
    Prepare medical waste dataset in YOLO format
    """
    
    def __init__(self, dataset_root):
        self.dataset_root = Path(dataset_root)
        self.dataset_root.mkdir(parents=True, exist_ok=True)
        
        # Define waste categories
        self.categories = {
            0: {'name': 'general_waste', 'description': 'Non-hazardous general medical waste'},
            1: {'name': 'infectious_waste', 'description': 'Infectious medical waste - biohazard'},
            2: {'name': 'sharps_hazardous', 'description': 'Sharps and hazardous medical waste'}
        }
        
        # Create directory structure
        self.create_directory_structure()
    
    def create_directory_structure(self):
        """
        Create YOLO dataset directory structure
        """
        structure = {
            'images': {'train': [], 'val': [], 'test': []},
            'labels': {'train': [], 'val': [], 'test': []},
            'metadata': None,
            'dataset.yaml': None
        }
        
        # Create main directories
        for split in ['train', 'val', 'test']:
            (self.dataset_root / 'images' / split).mkdir(parents=True, exist_ok=True)
            (self.dataset_root / 'labels' / split).mkdir(parents=True, exist_ok=True)
        
        print(f"✓ Directory structure created at: {self.dataset_root}")
    
    def create_dataset_yaml(self):
        """
        Create dataset.yaml configuration file for YOLO
        """
        dataset_yaml = {
            'path': str(self.dataset_root),
            'train': 'images/train',
            'val': 'images/val',
            'test': 'images/test',
            'nc': len(self.categories),
            'names': {k: v['name'] for k, v in self.categories.items()}
        }
        
        yaml_path = self.dataset_root / 'dataset.yaml'
        
        with open(yaml_path, 'w') as f:
            f.write("# Medical Waste Detection Dataset\n")
            f.write(f"path: {dataset_yaml['path']}\n")
            f.write(f"train: {dataset_yaml['train']}\n")
            f.write(f"val: {dataset_yaml['val']}\n")
            f.write(f"test: {dataset_yaml['test']}\n\n")
            f.write(f"nc: {dataset_yaml['nc']}\n")
            f.write("names:\n")
            for idx, name in dataset_yaml['names'].items():
                f.write(f"  {idx}: {name}\n")
        
        print(f"✓ Dataset YAML created: {yaml_path}")
        return yaml_path
    
    def create_sample_annotations(self):
        """
        Create sample annotation files in YOLO format
        These are templates for actual annotated data
        """
        sample_annotations = {
            'general_waste_sample.txt': '0 0.5 0.5 0.4 0.6',
            'infectious_waste_sample.txt': '1 0.3 0.4 0.5 0.7',
            'sharps_waste_sample.txt': '2 0.6 0.5 0.3 0.4'
        }
        
        for filename, annotation in sample_annotations.items():
            filepath = self.dataset_root / 'metadata' / filename
            filepath.parent.mkdir(parents=True, exist_ok=True)
            
            with open(filepath, 'w') as f:
                f.write(annotation)
        
        print("✓ Sample annotations created")
    
    def create_category_info(self):
        """
        Create detailed category information JSON
        """
        categories_info = {
            'dataset_name': 'Medical Waste Classification',
            'dataset_version': '1.0',
            'created_date': datetime.now().isoformat(),
            'categories': self.categories,
            'annotation_format': 'YOLO (class_id center_x center_y width height)',
            'image_requirements': {
                'min_resolution': [640, 640],
                'recommended_resolution': [1920, 1440],
                'formats': ['jpg', 'png', 'bmp']
            },
            'dataset_split': {
                'train': '70%',
                'val': '20%',
                'test': '10%'
            }
        }
        
        json_path = self.dataset_root / 'metadata' / 'categories.json'
        json_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(json_path, 'w') as f:
            json.dump(categories_info, f, indent=2)
        
        print(f"✓ Category information saved: {json_path}")
        return json_path
    
    def create_documentation(self):
        """
        Create dataset documentation
        """
        doc_content = """# Medical Waste Detection Dataset

## Overview
This dataset contains annotated images of medical waste for training YOLO object detection models.

## Dataset Structure
```
dataset/
├── images/
│   ├── train/      # Training images (70%)
│   ├── val/        # Validation images (20%)
│   └── test/       # Test images (10%)
├── labels/
│   ├── train/      # Training annotations
│   ├── val/        # Validation annotations
│   └── test/       # Test annotations
├── metadata/
│   ├── categories.json
│   └── dataset_stats.json
└── dataset.yaml    # YOLO configuration
```

## Waste Categories

### Category 0: General Waste (Green)
- Non-hazardous medical waste
- Paper, packaging, non-contaminated materials
- Color: Green (#00FF00)

### Category 1: Infectious Waste (Red)
- Biohazardous and infectious materials
- Cultures, contaminated items, body parts
- Color: Red (#FF0000)

### Category 2: Sharps/Hazardous Waste (Orange)
- Sharps: needles, syringes, scalpels
- Hazardous chemical waste
- Color: Orange (#FFA500)

## Annotation Format
Each image has a corresponding `.txt` file with annotations in YOLO format:
```
<class_id> <center_x> <center_y> <width> <height>
```

Where:
- `class_id`: 0, 1, or 2
- `center_x`, `center_y`: Normalized coordinates (0-1)
- `width`, `height`: Normalized dimensions (0-1)

## Data Collection Guidelines

### Camera Setup
- Resolution: Minimum 1280x960, recommended 1920x1440
- Lighting: Uniform, shadow-free illumination
- Angles: Multiple viewing angles per waste item
- Distance: 30-100 cm from waste object

### Imaging Requirements
- Waste items clearly visible and distinct
- Avoid overlapping objects (max 2-3 items per image)
- Include scale reference if possible
- Capture different waste states (intact, partial, scattered)

### Safety Considerations
- Use appropriate PPE when collecting data
- Sanitize cameras and equipment between sessions
- Handle waste according to hospital protocols
- Document any hazardous materials

## Annotation Process

### Using Labelimg
```bash
labelimg dataset/images/train dataset.yaml
```

### Using Roboflow
- Upload images to Roboflow
- Create bounding boxes for each waste item
- Assign appropriate class labels
- Export in YOLO format

## Statistics

### Current Dataset Stats
- Total Images: [To be filled]
- Training Images: [To be filled]
- Validation Images: [To be filled]
- Test Images: [To be filled]
- Total Annotations: [To be filled]

### Class Distribution
- General Waste: [%]
- Infectious Waste: [%]
- Sharps/Hazardous: [%]

## Training Configuration

### Recommended YOLO Model
```python
from ultralytics import YOLO

# Load pretrained model
model = YOLO('yolov8m.pt')

# Train
results = model.train(
    data='dataset.yaml',
    epochs=100,
    imgsz=640,
    device=0,
    batch=16,
    patience=50
)
```

### Expected Performance
- mAP@50: 85%+
- mAP@50-95: 60%+
- Training time: 2-4 hours (GPU)

## Quality Control

### Validation Checklist
- [ ] All images properly annotated
- [ ] No missing annotations
- [ ] Annotations correctly aligned
- [ ] No overlapping classes
- [ ] Images properly distributed across splits
- [ ] Metadata files complete

## Dataset Citation
When using this dataset, please cite:
```
Medical Waste Detection Dataset (2024)
Collected by: [Institution Name]
License: [License Type]
```

## Troubleshooting

### Common Issues

1. **Missing Annotations**
   - Verify all images have corresponding .txt files
   - Check file naming matches: image.jpg → image.txt

2. **Incorrect Annotation Format**
   - Ensure coordinates are normalized (0-1)
   - Verify class IDs are 0, 1, or 2

3. **Class Imbalance**
   - Use data augmentation during training
   - Implement weighted loss functions

## Next Steps

1. Collect and annotate 1000+ images per class
2. Validate dataset quality
3. Train YOLO model
4. Evaluate on test set
5. Fine-tune hyperparameters
6. Deploy to robot

## References

- YOLO Documentation: https://docs.ultralytics.com
- Medical Waste Guidelines: WHO, CDC
- Dataset Best Practices: Roboflow Blog

"""
        
        doc_path = self.dataset_root / 'DATASET_README.md'
        
        with open(doc_path, 'w') as f:
            f.write(doc_content)
        
        print(f"✓ Documentation created: {doc_path}")
        return doc_path
    
    def create_data_collection_guide(self):
        """
        Create data collection guidelines
        """
        guide_content = """# Data Collection Guide for Medical Waste Detection

## Safety First
- Always wear appropriate PPE (gloves, mask, eye protection)
- Handle waste according to hospital protocols
- Never collect data from active infectious wards without permission
- Document any incidents

## Equipment Setup

### Camera Specifications
- Resolution: 1920x1440 or higher
- Autofocus: Enabled
- White balance: Automatic
- ISO: Auto (max 3200)
- Framerate: 30 FPS

### Lighting Setup
- LED panel lights on both sides
- Diffused light to avoid harsh shadows
- Color temperature: 5000K (daylight)
- Minimum illumination: 500 lux

### Positioning
- Camera height: 60-90 cm from ground
- Angle: 30-45 degrees above horizontal
- Distance: 50-80 cm from waste
- Stable tripod or mounting

## Collection Workflow

### Per Imaging Session
1. Setup and calibrate camera
2. Prepare waste samples
3. Record with multiple angles
4. Capture at least 10 images per waste item
5. Document metadata (date, time, location, waste type)
6. Sanitize equipment

### Data Organization
```
collection_session_YYYY_MM_DD/
├── general_waste_001-100.jpg
├── infectious_waste_001-100.jpg
├── sharps_waste_001-100.jpg
├── metadata.json
└── collection_log.txt
```

## Image Requirements

### Composition
- Single or few waste items per image
- Waste fills 30-70% of image
- Clear background (preferably white)
- Waste clearly visible, no blur

### Variations
- Different angles (top, side, 45°)
- Different scales (close-up, medium, far)
- Different lighting conditions
- Different backgrounds

## Metadata Recording

```json
{
  "image_id": "general_waste_001",
  "collection_date": "2024-06-11",
  "collection_time": "14:30:00",
  "waste_category": 0,
  "waste_description": "Medical gauze",
  "image_path": "general_waste_001.jpg",
  "camera_settings": {
    "resolution": "1920x1440",
    "iso": 400,
    "shutter_speed": "1/125"
  },
  "location": "Hospital Lab - Room 205",
  "collector": "Technician Name"
}
```

## Quality Targets

### Target Collection Volumes
- General Waste: 500-800 images
- Infectious Waste: 400-600 images
- Sharps/Hazardous: 400-600 images
- **Total: 1500-2000 images**

### Split Distribution
- Training: 70% (1050-1400 images)
- Validation: 20% (300-400 images)
- Test: 10% (150-200 images)

### Annotation Guidelines

1. **Bounding Box Rules**
   - Tight fit around waste item
   - Include entire object
   - Exclude large empty spaces

2. **Multi-item Images**
   - Annotate each distinct item
   - Use different class IDs if mixed waste
   - Prefer single-item images

3. **Edge Cases**
   - Partially visible items: Include if >70% visible
   - Overlapping items: Create separate boxes
   - Very small items: Ensure minimum 20px height

## Schedule

### Phase 1: Initial Collection (Weeks 1-2)
- Target: 300 images per class
- Location: Laboratory areas
- Review and clean data

### Phase 2: Expansion (Weeks 3-4)
- Target: 500 images per class
- Locations: Multiple hospital areas
- Quality assurance

### Phase 3: Augmentation (Weeks 5-6)
- Target: 800 images per class
- Edge cases and variations
- Final dataset preparation

## Challenges & Solutions

### Challenge: Class Imbalance
**Solution**: Oversample minority classes during training

### Challenge: Poor Lighting
**Solution**: Use consistent LED lighting setup

### Challenge: Motion Blur
**Solution**: Fast shutter speed (1/125s or faster)

### Challenge: Similar Objects
**Solution**: Collect from different backgrounds

## Quality Assurance

### Post-Collection Review
- [ ] All images properly named
- [ ] Metadata complete
- [ ] No duplicate images
- [ ] Sufficient variation in angles
- [ ] Good image quality (sharp, well-lit)
- [ ] Realistic waste distribution

### Dataset Validation
- [ ] All images have annotations
- [ ] Annotation format correct
- [ ] No overlapping categories
- [ ] Balanced class distribution
- [ ] Proper train/val/test split

## Data Storage & Backup

- Primary storage: NAS with RAID-6
- Backup: Cloud storage (encrypted)
- Metadata backup: Git repository
- Retention: At least 5 years

## Documentation

Keep records of:
- Collection date and time
- Location and collector
- Camera settings used
- Any issues encountered
- Waste handling protocols followed

"""
        
        guide_path = self.dataset_root / 'DATA_COLLECTION_GUIDE.md'
        
        with open(guide_path, 'w') as f:
            f.write(guide_content)
        
        print(f"✓ Data collection guide created: {guide_path}")
        return guide_path
    
    def generate_dataset_summary(self):
        """
        Generate a summary of the prepared dataset structure
        """
        summary = {
            'dataset_path': str(self.dataset_root),
            'created_date': datetime.now().isoformat(),
            'categories': self.categories,
            'directory_structure': {
                'images': {
                    'train': str(self.dataset_root / 'images' / 'train'),
                    'val': str(self.dataset_root / 'images' / 'val'),
                    'test': str(self.dataset_root / 'images' / 'test')
                },
                'labels': {
                    'train': str(self.dataset_root / 'labels' / 'train'),
                    'val': str(self.dataset_root / 'labels' / 'val'),
                    'test': str(self.dataset_root / 'labels' / 'test')
                }
            },
            'files_created': {
                'dataset.yaml': 'YOLO configuration file',
                'categories.json': 'Category metadata',
                'DATASET_README.md': 'Dataset documentation',
                'DATA_COLLECTION_GUIDE.md': 'Collection guidelines'
            }
        }
        
        summary_path = self.dataset_root / 'metadata' / 'dataset_summary.json'
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        return summary


def main():
    parser = argparse.ArgumentParser(description='Prepare Medical Waste Detection Dataset')
    parser.add_argument(
        '--dataset-root',
        type=str,
        default='./waste_detection_dataset',
        help='Root directory for dataset'
    )
    
    args = parser.parse_args()
    
    print("="*60)
    print("Medical Waste Detection Dataset Preparation")
    print("="*60)
    
    preparer = WasteDatasetPreparer(args.dataset_root)
    
    # Create dataset structure and files
    preparer.create_dataset_yaml()
    preparer.create_category_info()
    preparer.create_sample_annotations()
    preparer.create_documentation()
    preparer.create_data_collection_guide()
    summary = preparer.generate_dataset_summary()
    
    print("\n" + "="*60)
    print("Dataset Preparation Complete!")
    print("="*60)
    print(f"\nDataset Location: {args.dataset_root}")
    print("\nNext Steps:")
    print("1. Collect medical waste images following DATA_COLLECTION_GUIDE.md")
    print("2. Place images in images/train, images/val, images/test directories")
    print("3. Create annotations in labels/ directories in YOLO format")
    print("4. Run dataset validation")
    print("5. Train YOLO model using dataset.yaml")
    print("\nFor detailed instructions, see DATASET_README.md")
    print("="*60 + "\n")


if __name__ == '__main__':
    main()
