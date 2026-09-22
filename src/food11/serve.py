import io
import os

import mlflow
import numpy as np
import torch

from fastapi import FastAPI, File, UploadFile, HTTPException
from PIL import Image
from torchvision import transforms


# --------------------------------------------------
# 1. MLflow connection
# --------------------------------------------------

MLFLOW_TRACKING_URI = os.getenv(
    "MLFLOW_TRACKING_URI",
    "http://127.0.0.1:5000"
)

mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)


# --------------------------------------------------
# 2. Load the registered champion model
# --------------------------------------------------

MODEL_URI = "models:/food11@champion"

model = mlflow.pyfunc.load_model(MODEL_URI)


# --------------------------------------------------
# 3. Food-11 class names
# --------------------------------------------------

CLASS_NAMES = [
    "Bread",
    "Dairy product",
    "Dessert",
    "Egg",
    "Fried food",
    "Meat",
    "Noodles-Pasta",
    "Rice",
    "Seafood",
    "Soup",
    "Vegetable-Fruit",
]


# --------------------------------------------------
# 4. Image preprocessing
#    This matches the preprocessing in train.py
# --------------------------------------------------

preprocess = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])


# --------------------------------------------------
# 5. Create the FastAPI application
# --------------------------------------------------

app = FastAPI()


# --------------------------------------------------
# 6. Health endpoint
# --------------------------------------------------

@app.get("/health")
def health():
    return {"status": "ok"}


# --------------------------------------------------
# 7. Prediction endpoint
# --------------------------------------------------

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    try:
        # Read the uploaded image
        contents = await file.read()

        # Convert the uploaded bytes into a PIL image
        image = Image.open(io.BytesIO(contents)).convert("RGB")

        # Apply the same preprocessing used during training
        image_tensor = preprocess(image)

        # Add a batch dimension:
        # [3, 224, 224] -> [1, 3, 224, 224]
        image_tensor = image_tensor.unsqueeze(0)

        # MLflow pyfunc receives numpy data
        input_array = image_tensor.numpy()

        # Run the model
        output = model.predict(input_array)

        # Make sure the result is a numpy array
        output = np.asarray(output)

        # Convert logits to a PyTorch tensor
        logits = torch.tensor(output)

        # Turn raw model outputs into probabilities
        probabilities = torch.softmax(logits, dim=1)

        # Find the class with the highest probability
        confidence, predicted_index = torch.max(
            probabilities,
            dim=1
        )

        predicted_class = CLASS_NAMES[predicted_index.item()]

        return {
            "category": predicted_class,
            "confidence": float(confidence.item())
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )