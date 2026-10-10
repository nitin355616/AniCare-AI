# AniCare AI — Vision Model Training & Benchmarking Suite

This package implements reproducible training, hyperparameter exploration, confidence calibration, and ONNX export for AniCare AI's bovine visual condition classifier.

## Architecture & Workflow

```
raw/lumpy_skin_disease (1,024 images)
          │
          ▼
processed/manifest.json (906 clean samples after de-duplication)
          │
  ┌───────┴───────┬───────────────┐
  ▼               ▼               ▼
Train (633)     Val (135)     Test (138) [Untouched]
  │               │
  │               ▼
  │      Model Selection:
  │      Benchmark Architectures (MobileNetV3 vs EfficientNet-B0)
  │      Benchmark Loss Formulations (Focal Loss vs Weighted CE)
  │      Two-Phase Transfer Learning (Head training -> Top layer fine-tuning)
  │               │
  │               ▼
  │      Best Validation Model Selected
  │               │
  │               ▼
  │      Confidence Calibration (Temperature Scaling)
  │               │
  └───────────────┼───────────────┐
                  ▼               ▼
        Final Evaluation ONCE on Untouched Test Split (138 images)
                  │
                  ▼
        ONNX Export & Parity Verification
                  │
                  ▼
        RealVisionInferenceEngine Activation
```

## Modules

- `config.py`: Centralized hyperparameters and path configurations.
- `transforms.py`: Clinical pathology-preserving augmentations for training, deterministic resizing for evaluation.
- `dataset.py`: PyTorch `Dataset` loading images directly from verified manifest records with split isolation.
- `losses.py`: Class-weighted cross entropy and focal loss formulations.
- `model.py`: Model factory supporting MobileNetV3-Large and EfficientNet-B0 with layer freezing/unfreezing controls.
- `train.py`: Two-phase training loop with cosine learning rate scheduling and validation-checkpoint saving.
- `evaluate.py`: Evaluation pipeline capturing accuracy, macro F1, sensitivity, specificity, and full false-negative failure case audits.
- `calibration.py`: Expected Calibration Error (ECE) and Platt/Guo Temperature Scaling.
- `utils.py`: Deterministic seeding, confusion matrix rendering, and ONNX parity testing.
