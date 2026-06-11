#!/usr/bin/env python3
"""
YOLO Model Training Script for Medical Waste Detection
Trains YOLOv8 model on medical waste dataset
"""

import argparse
import yaml
from pathlib import Path
from ultralytics import YOLO
import torch
import matplotlib.pyplot as plt
import json
from datetime import datetime

class YOLOTrainer:
    """
    Train YOLO model for medical waste detection
    """
    
    def __init__(self, config_path):
        self.config_path = Path(config_path)
        self.load_config()
        self.setup_paths()
    
    def load_config(self):
        """Load training configuration"""
        with open(self.config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        print(f"✓ Configuration loaded from {self.config_path}")
    
    def setup_paths(self):
        """Setup output directories"""
        self.output_dir = Path(self.config.get('output_dir', './runs/detect'))
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.models_dir = Path(self.config.get('models_dir', './models'))
        self.models_dir.mkdir(parents=True, exist_ok=True)
    
    def train(self):
        """Train YOLO model"""
        print("\n" + "="*60)
        print("Starting YOLO Training")
        print("="*60)
        
        # Load model
        model_size = self.config.get('model_size', 'm')
        model_name = f'yolov8{model_size}.pt'
        
        print(f"\n📦 Loading base model: {model_name}")
        model = YOLO(model_name)
        
        # Check GPU availability
        device = 0 if torch.cuda.is_available() else 'cpu'
        print(f"🖥️  Using device: {'CUDA' if device == 0 else 'CPU'}")
        
        # Prepare training parameters
        train_params = {
            'data': self.config['data_yaml'],
            'epochs': self.config.get('epochs', 100),
            'imgsz': self.config.get('imgsz', 640),
            'batch': self.config.get('batch_size', 16),
            'device': device,
            'patience': self.config.get('patience', 50),
            'save': True,
            'save_period': self.config.get('save_period', 10),
            'project': str(self.output_dir),
            'name': self.config.get('experiment_name', 'waste_detection'),
            'exist_ok': False,
            'verbose': True,
            'seed': self.config.get('seed', 42),
            'deterministic': True,
            'single_cls': False,
            'rect': False,
            'cos_lr': False,
            'close_mosaic': self.config.get('close_mosaic', 10),
            'augment': self.config.get('augment', True),
        }
        
        # Add optimizer
        if 'optimizer' in self.config:
            train_params['optimizer'] = self.config['optimizer']
        
        # Print training configuration
        print("\n📋 Training Parameters:")
        for key, value in train_params.items():
            if key not in ['data']:
                print(f"  {key}: {value}")
        
        print(f"\n🚀 Starting training with data from: {train_params['data']}")
        
        try:
            # Train model
            results = model.train(**train_params)
            
            print("\n✓ Training completed successfully!")
            
            # Save training results
            self.save_training_results(results, train_params)
            
            # Evaluate model
            self.evaluate_model(model, train_params)
            
            # Save final model
            final_model_path = self.models_dir / 'waste_detector_final.pt'
            model.save(final_model_path)
            print(f"\n✓ Final model saved to: {final_model_path}")
            
            return results
            
        except Exception as e:
            print(f"\n❌ Training failed: {e}")
            raise
    
    def evaluate_model(self, model, train_params):
        """Evaluate trained model on test set"""
        print("\n" + "="*60)
        print("Evaluating Model")
        print("="*60)
        
        try:
            # Run validation
            print("\n🔍 Running validation...")
            val_results = model.val()
            
            # Print validation metrics
            print("\n📊 Validation Results:")
            print(f"  mAP@50: {val_results.results_dict.get('metrics/mAP50', 'N/A'):.3f}")
            print(f"  mAP@50-95: {val_results.results_dict.get('metrics/mAP50-95', 'N/A'):.3f}")
            
            return val_results
            
        except Exception as e:
            print(f"Evaluation warning: {e}")
            return None
    
    def save_training_results(self, results, params):
        """Save training results and metadata"""
        results_dict = {
            'training_date': datetime.now().isoformat(),
            'parameters': params,
            'results': {
                'epochs_completed': params['epochs'],
                'batch_size': params['batch'],
                'image_size': params['imgsz'],
            }
        }
        
        results_file = self.output_dir / 'training_results.json'
        with open(results_file, 'w') as f:
            json.dump(results_dict, f, indent=2, default=str)
        
        print(f"\n✓ Training results saved to: {results_file}")
    
    def export_model(self, model_path):
        """Export model to different formats"""
        print("\n" + "="*60)
        print("Exporting Model")
        print("="*60)
        
        model = YOLO(model_path)
        
        export_formats = {
            'onnx': 'ONNX format for deployment',
            'torchscript': 'TorchScript for ROS2',
            'tflite': 'TensorFlow Lite for edge devices'
        }
        
        for fmt, description in export_formats.items():
            try:
                print(f"\n📦 Exporting to {fmt}: {description}")
                exported_path = model.export(format=fmt)
                print(f"  ✓ Exported to: {exported_path}")
            except Exception as e:
                print(f"  ⚠️  Export to {fmt} failed: {e}")


def create_default_config(config_path):
    """Create default training configuration"""
    default_config = {
        'data_yaml': './waste_detection_dataset/dataset.yaml',
        'model_size': 'm',  # nano(n), small(s), medium(m), large(l), xlarge(x)
        'epochs': 100,
        'imgsz': 640,
        'batch_size': 16,
        'patience': 50,
        'save_period': 10,
        'seed': 42,
        'experiment_name': 'waste_detection_v1',
        'output_dir': './runs/detect',
        'models_dir': './models',
        'close_mosaic': 10,
        'augment': True,
        'optimizer': 'SGD',
        'lr0': 0.01,
        'lrf': 0.01,
        'momentum': 0.937,
        'weight_decay': 0.0005,
        'warmup_epochs': 3.0,
        'warmup_momentum': 0.8,
        'box': 7.5,
        'cls': 0.5,
        'cls_pw': 1.0,
        'obj': 1.0,
        'obj_pw': 1.0,
        'iou': 0.7,
        'fl_gamma': 0.0
    }
    
    with open(config_path, 'w') as f:
        yaml.dump(default_config, f, default_flow_style=False)
    
    print(f"✓ Default configuration created: {config_path}")
    return default_config


def predict_on_image(model_path, image_path):
    """Run inference on single image"""
    print("\n" + "="*60)
    print("Running Inference")
    print("="*60)
    
    model = YOLO(model_path)
    
    print(f"\n🖼️  Processing image: {image_path}")
    
    results = model.predict(
        source=image_path,
        conf=0.5,
        save=True,
        save_txt=True,
        verbose=True
    )
    
    print("\n✓ Inference completed")
    return results


def predict_on_video(model_path, video_path):
    """Run inference on video"""
    print("\n" + "="*60)
    print("Running Video Inference")
    print("="*60)
    
    model = YOLO(model_path)
    
    print(f"\n🎥 Processing video: {video_path}")
    
    results = model.predict(
        source=video_path,
        conf=0.5,
        save=True,
        device=0 if torch.cuda.is_available() else 'cpu',
        verbose=False
    )
    
    print("\n✓ Video inference completed")
    return results


def main():
    parser = argparse.ArgumentParser(description='Train YOLO for Medical Waste Detection')
    
    parser.add_argument(
        '--train',
        action='store_true',
        help='Train the model'
    )
    parser.add_argument(
        '--config',
        type=str,
        default='./config/yolo_training_config.yaml',
        help='Path to training configuration file'
    )
    parser.add_argument(
        '--export',
        type=str,
        help='Export trained model from checkpoint'
    )
    parser.add_argument(
        '--predict',
        type=str,
        help='Run inference on image'
    )
    parser.add_argument(
        '--predict-video',
        type=str,
        help='Run inference on video'
    )
    parser.add_argument(
        '--model',
        type=str,
        default='./models/waste_detector_final.pt',
        help='Path to trained model'
    )
    parser.add_argument(
        '--create-config',
        action='store_true',
        help='Create default configuration file'
    )
    
    args = parser.parse_args()
    
    # Create default config if requested
    if args.create_config:
        create_default_config(args.config)
        return
    
    # Train model
    if args.train:
        trainer = YOLOTrainer(args.config)
        trainer.train()
    
    # Export model
    elif args.export:
        trainer = YOLOTrainer(args.config)
        trainer.export_model(args.export)
    
    # Predict on image
    elif args.predict:
        predict_on_image(args.model, args.predict)
    
    # Predict on video
    elif args.predict_video:
        predict_on_video(args.model, args.predict_video)
    
    else:
        print("Please specify an action: --train, --export, --predict, or --predict-video")
        parser.print_help()


if __name__ == '__main__':
    main()
