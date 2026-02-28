try:
    from dotenv import load_dotenv
    print("python-dotenv is installed successfully!")
except ImportError:
    print("python-dotenv is not installed.")


from google import genai

# The client gets the API key from the environment variable `GEMINI_API_KEY`.
client = genai.Client()

response = client.models.generate_content(
    model="gemini-3-flash-preview", contents="Explain how AI works in a few words"
)
print(response.text)