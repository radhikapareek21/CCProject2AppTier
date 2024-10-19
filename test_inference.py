import sys
from model.face_recognition import face_match  # Importing the face_match function

# Test image
test_image = 'test_000.jpg'

# Perform face matching
result = face_match(test_image, 'model/data.pt')  # Using 'data.pt' for pre-saved embeddings

# Output the result
print(f"Inference result: {result[0]}, Distance: {result[1]}")
