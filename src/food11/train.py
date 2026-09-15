import argparse
from pathlib import Path

import mlflow
import mlflow.pytorch
import torch
from torch import nn
from torch.utils.data import DataLoader
from torchvision import datasets, transforms, models
from torchvision.models import ResNet18_Weights


# Tell MLflow where the tracking server is
mlflow.set_tracking_uri("http://127.0.0.1:5000")

# All runs from this script will go into the "food11" experiment
mlflow.set_experiment("food11")


def get_data_loaders(dataset_name, batch_size):
    if dataset_name == "mini":
        data_root = Path("data/food11_processed_mini")
    else:
        data_root = Path("data/food11_processed")

    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
    ])

    train_dataset = datasets.ImageFolder(
        data_root / "training",
        transform=transform
    )

    val_dataset = datasets.ImageFolder(
        data_root / "validation",
        transform=transform
    )

    test_dataset = datasets.ImageFolder(
        data_root / "evaluation",
        transform=transform
    )

    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=0
    )

    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=0
    )

    test_loader = DataLoader(
        test_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=0
    )

    return train_loader, val_loader, test_loader


def evaluate(model, loader, criterion, device):
    model.eval()

    total_loss = 0.0
    correct = 0
    total = 0

    with torch.no_grad():
        for images, labels in loader:
            images = images.to(device)
            labels = labels.to(device)

            outputs = model(images)
            loss = criterion(outputs, labels)

            total_loss += loss.item() * images.size(0)

            predictions = outputs.argmax(dim=1)

            correct += (predictions == labels).sum().item()
            total += labels.size(0)

    average_loss = total_loss / total
    accuracy = correct / total

    return average_loss, accuracy


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--dataset",
        choices=["mini", "processed"],
        default="mini"
    )

    parser.add_argument(
        "--epochs",
        type=int,
        default=5
    )

    parser.add_argument(
        "--lr",
        type=float,
        default=0.001
    )

    parser.add_argument(
        "--batch-size",
        type=int,
        default=32
    )

    args = parser.parse_args()

    # CPU will be used with your current PyTorch installation
    device = torch.device("cpu")

    print("Using device:", device)

    train_loader, val_loader, test_loader = get_data_loaders(
        args.dataset,
        args.batch_size
    )

    # Load pretrained ResNet18
    weights = ResNet18_Weights.DEFAULT
    model = models.resnet18(weights=weights)

    # Replace the final 1000-class layer with an 11-class layer
    model.fc = nn.Linear(model.fc.in_features, 11)

    model = model.to(device)

    criterion = nn.CrossEntropyLoss()

    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=args.lr
    )

    with mlflow.start_run():

        # Parameters stay fixed throughout the run
        mlflow.log_params({
            "dataset": args.dataset,
            "epochs": args.epochs,
            "lr": args.lr,
            "batch_size": args.batch_size,
            "model": "resnet18"
        })

        for epoch in range(args.epochs):
            model.train()

            total_train_loss = 0.0
            total_train_samples = 0

            for images, labels in train_loader:
                images = images.to(device)
                labels = labels.to(device)

                optimizer.zero_grad()

                outputs = model(images)

                loss = criterion(outputs, labels)

                loss.backward()

                optimizer.step()

                total_train_loss += loss.item() * images.size(0)
                total_train_samples += images.size(0)

            train_loss = total_train_loss / total_train_samples

            val_loss, val_accuracy = evaluate(
                model,
                val_loader,
                criterion,
                device
            )

            print(
                f"Epoch {epoch + 1}/{args.epochs} | "
                f"Train Loss: {train_loss:.4f} | "
                f"Val Loss: {val_loss:.4f} | "
                f"Val Accuracy: {val_accuracy:.4f}"
            )

            # Metrics change from epoch to epoch
            mlflow.log_metric(
                "train_loss",
                train_loss,
                step=epoch
            )

            mlflow.log_metric(
                "val_loss",
                val_loss,
                step=epoch
            )

            mlflow.log_metric(
                "val_accuracy",
                val_accuracy,
                step=epoch
            )

        test_loss, test_accuracy = evaluate(
            model,
            test_loader,
            criterion,
            device
        )

        print(f"Final Test Accuracy: {test_accuracy:.4f}")

        mlflow.log_metric(
            "test_accuracy",
            test_accuracy
        )

        mlflow.pytorch.log_model(
        model,
        name="model",
        serialization_format="pickle"
        )


if __name__ == "__main__":
    main()