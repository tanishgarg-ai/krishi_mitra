# python
import argparse
from pathlib import Path
import os
import torch
import torch.nn as nn
from torchvision import models, transforms, datasets
from PIL import Image


# Match the architecture used during training
class ResNet50V2(nn.Module):
    def __init__(self, num_classes: int):
        super().__init__()
        self.model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V2)
        num_ftrs = self.model.fc.in_features
        self.model.fc = nn.Sequential(
            nn.Linear(num_ftrs, 256),
            nn.GELU(),
            nn.Dropout(0.5),
            nn.Linear(256, num_classes),
        )

    def forward(self, x):
        return self.model(x)


# Use the same validation/test transforms as training
VAL_TEST_TRANSFORM = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225])
])


def load_model_wheat(weights_path: str, num_classes: int, device: torch.device) -> nn.Module:
    model = ResNet50V2(num_classes=num_classes).to(device)
    state = torch.load(weights_path, map_location=device)
    # Support checkpoints saved as either full state_dict or {"state_dict": ...}
    if isinstance(state, dict) and "state_dict" in state and isinstance(state["state_dict"], dict):
        state = state["state_dict"]
        # If keys are prefixed (e.g., "model."), try to strip the top-level prefix
        if not any(k.startswith("model.fc") or k.startswith("fc") for k in state.keys()):
            stripped = {}
            for k, v in state.items():
                # remove a possible leading "model." or similar
                stripped[k.split(".", 1)[-1] if "." in k else k] = v
            state = stripped
    model.load_state_dict(state, strict=False)
    model.eval()
    return model


@torch.no_grad()
def predict_image_wheat(image_path: str, model: nn.Module, class_names: list[str], device: torch.device) -> str:
    image = Image.open(image_path).convert("RGB")
    tensor = VAL_TEST_TRANSFORM(image).unsqueeze(0).to(device)
    outputs = model(tensor)
    if isinstance(outputs, (list, tuple)):
        outputs = outputs[0]
    pred_idx = int(outputs.argmax(dim=1).item())
    return class_names[pred_idx]

class_names = ['Aphid', 'Black Rust', 'Blast', 'Brown Rust', 'Common Root Rot', 'Fusarium Head Blight', 'Healthy',
           'Leaf Blight', 'Mildew', 'Mite', 'Septoria', 'Smut', 'Stem fly', 'Tan spot', 'Yellow Rust']

wheat_model_path = os.getenv("WHEAT_MODEL_PATH")