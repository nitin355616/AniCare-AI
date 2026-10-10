"""
AniCare AI — Image Preprocessing & Controlled Transforms
Enforces ImageNet normalization, 224x224 input sizing, and morphological-preserving augmentations.
"""

from typing import Tuple
import torchvision.transforms as transforms


def get_train_transforms(image_size: int = 224) -> transforms.Compose:
    """
    Controlled data augmentation for training split.
    Guarantees clinical pathology preservation:
    - Avoids severe shear, extreme hue distortions, or cutout that obliterate nodular morphology.
    """
    return transforms.Compose([
        transforms.Resize((image_size, image_size)),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomRotation(degrees=10),
        transforms.ColorJitter(brightness=0.10, contrast=0.10),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
    ])


def get_robust_train_transforms(image_size: int = 224) -> transforms.Compose:
    """
    Milestone 6: Enhanced biologically conservative robust augmentation pipeline.
    Directly addresses failure modes identified in FALSE_NEGATIVE_ANALYSIS:
    - RandomResizedCrop (scale 0.85-1.0): Addresses small lesion / background dilution.
    - GaussianBlur (3x3 kernel, sigma 0.1-1.0): Simulates motion blur & compression softness.
    - Controlled ColorJitter (brightness 0.15, contrast 0.15): Simulates barn shadows.
    - Preserves exact morphological boundaries (no aggressive hue or cutout).
    """
    return transforms.Compose([
        transforms.RandomResizedCrop(image_size, scale=(0.85, 1.0), ratio=(0.95, 1.05)),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomRotation(degrees=12),
        transforms.ColorJitter(brightness=0.15, contrast=0.15),
        transforms.GaussianBlur(kernel_size=(3, 3), sigma=(0.1, 1.0)),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
    ])


def get_eval_transforms(image_size: int = 224) -> transforms.Compose:
    """
    Deterministic preprocessing for validation and test splits.
    Zero random distortion; identical to production inference pipeline.
    """
    return transforms.Compose([
        transforms.Resize((image_size, image_size)),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
    ])
