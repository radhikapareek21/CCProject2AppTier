import torch
from model import FaceRecognitionModel  # Assuming this is your model

# Load the model
model = FaceRecognitionModel()
model.load_state_dict(torch.load('model/model_weights.pth'))  # Ensure model_weights.pth exists in the 'model' folder
model.eval()

# Test inference with the test image
test_image = 'test_000.jpg'  # The test image file in your directory
result = model.infer(test_image)  # Assuming your model has an infer function
print("Inference result:", result)
