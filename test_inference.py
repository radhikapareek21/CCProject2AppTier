import torch
from model import FaceRecognitionModel  # Assuming this is your model

# Load the model
model = FaceRecognitionModel()
model.load_state_dict(torch.load('model_weights.pth'))  # Replace with correct path
model.eval()

# Test inference
test_image = '/path/to/test_image.jpg'  # Replace with actual image path
result = model.infer(test_image)  # Assuming your model has an infer function
print("Inference result:", result)