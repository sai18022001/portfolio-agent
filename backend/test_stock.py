import requests
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).parent.parent / ".env")

api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
print(f"API Key loaded: {api_key}")

url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=AAPL&apikey={api_key}"
response = requests.get(url)
data = response.json()
print("Response:", data)