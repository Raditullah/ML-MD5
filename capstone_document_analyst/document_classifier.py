"""Capstone Track B (M1) - CNN document-type classifier via transfer learning.

Demonstrates the M1 requirement (trained deep learning model for
perception/classification): a pretrained ResNet18 backbone (ImageNet
weights, frozen) with a small trainable linear head, fine-tuned on a tiny
synthetic dataset that distinguishes "text-heavy" document page renders
from "chart/figure-heavy" page renders -- the kind of routing decision a
real document pipeline needs before deciding whether to run OCR/text
extraction or a vision-based chart parser on a given page.

This runs entirely on CPU; the synthetic images are generated
procedurally so the lab needs no external dataset download.
"""
import numpy as np
import torch
import torch.nn as nn
from PIL import Image, ImageDraw
from torchvision import models, transforms

IMG_SIZE = 128
CLASSES = ["text_heavy", "chart_heavy"]


def _make_text_heavy_image(seed):
    rng = np.random.RandomState(seed)
    img = Image.new("L", (IMG_SIZE, IMG_SIZE), color=255)
    draw = ImageDraw.Draw(img)
    # Simulate dense horizontal text lines
    y = 10
    while y < IMG_SIZE - 10:
        line_width = rng.randint(60, IMG_SIZE - 20)
        draw.line([(10, y), (10 + line_width, y)], fill=0, width=2)
        y += rng.randint(6, 10)
    return img.convert("RGB")


def _make_chart_heavy_image(seed):
    rng = np.random.RandomState(seed)
    img = Image.new("L", (IMG_SIZE, IMG_SIZE), color=255)
    draw = ImageDraw.Draw(img)
    # Simulate a bar chart: axes + a few rectangular bars
    draw.line([(15, 15), (15, IMG_SIZE - 15)], fill=0, width=2)  # y-axis
    draw.line([(15, IMG_SIZE - 15), (IMG_SIZE - 10, IMG_SIZE - 15)], fill=0, width=2)  # x-axis
    x = 25
    for _ in range(rng.randint(3, 6)):
        bar_h = rng.randint(20, IMG_SIZE - 40)
        bar_w = rng.randint(8, 15)
        draw.rectangle([x, IMG_SIZE - 15 - bar_h, x + bar_w, IMG_SIZE - 15], fill=0)
        x += bar_w + rng.randint(5, 10)
    return img.convert("RGB")


def make_synthetic_dataset(n_per_class=40, seed_offset=0):
    images, labels = [], []
    for i in range(n_per_class):
        images.append(_make_text_heavy_image(seed_offset + i))
        labels.append(0)
        images.append(_make_chart_heavy_image(seed_offset + 1000 + i))
        labels.append(1)
    return images, labels


def build_model():
    """ResNet18 pretrained on ImageNet, frozen backbone + trainable head."""
    model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
    for param in model.parameters():
        param.requires_grad = False
    model.fc = nn.Linear(model.fc.in_features, len(CLASSES))
    return model


def train(epochs=5):
    preprocess = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    train_images, train_labels = make_synthetic_dataset(n_per_class=40, seed_offset=0)
    val_images, val_labels = make_synthetic_dataset(n_per_class=10, seed_offset=5000)

    X_train = torch.stack([preprocess(img) for img in train_images])
    y_train = torch.tensor(train_labels)
    X_val = torch.stack([preprocess(img) for img in val_images])
    y_val = torch.tensor(val_labels)

    model = build_model()
    optimizer = torch.optim.Adam(model.fc.parameters(), lr=1e-3)
    criterion = nn.CrossEntropyLoss()

    model.train()
    for epoch in range(epochs):
        optimizer.zero_grad()
        logits = model(X_train)
        loss = criterion(logits, y_train)
        loss.backward()
        optimizer.step()

        model.eval()
        with torch.no_grad():
            val_logits = model(X_val)
            val_acc = (val_logits.argmax(1) == y_val).float().mean().item()
        model.train()
        print(f"Epoch {epoch+1}/{epochs} - loss={loss.item():.4f} - val_acc={val_acc:.2%}")

    torch.save(model.state_dict(), "document_classifier.pt")
    print("Saved: document_classifier.pt")
    return model


def classify(model, pil_image):
    preprocess = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    model.eval()
    with torch.no_grad():
        x = preprocess(pil_image).unsqueeze(0)
        logits = model(x)
        probs = torch.softmax(logits, dim=1)[0]
        pred_idx = probs.argmax().item()
    return CLASSES[pred_idx], probs[pred_idx].item()


if __name__ == "__main__":
    print("Training document-type classifier (ResNet18 transfer learning)...")
    model = train(epochs=5)

    print("\n=== Inference on fresh synthetic samples ===")
    test_images, test_labels = make_synthetic_dataset(n_per_class=3, seed_offset=9999)
    correct = 0
    for img, true_label in zip(test_images, test_labels):
        pred_class, confidence = classify(model, img)
        true_class = CLASSES[true_label]
        match = "OK" if pred_class == true_class else "WRONG"
        if pred_class == true_class:
            correct += 1
        print(f"[{match}] true={true_class:12s} pred={pred_class:12s} conf={confidence:.2%}")
    print(f"\nTest accuracy: {correct}/{len(test_images)}")
