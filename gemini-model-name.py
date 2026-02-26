import google.generativeai as genai
import os

# Configure the API key (replace with your setup, e.g., environment variable)
# You can get an API key from Google AI Studio: https://aistudio.google.com/app/apikey
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# Instantiate the model, specifying the name (e.g., 'gemini-1.5-flash')
model = genai.GenerativeModel(model_name="Imagen 4 Fast Generate")

# Access the model name
print(f"The model name is: {model.model_name}") 
# Output: The model name is: models/gemini-1.5-flash
