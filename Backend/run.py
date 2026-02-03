from app import create_app
from dotenv import load_dotenv
import os

# Load environment variables from .flaskenv
load_dotenv('.flaskenv')

app = create_app()

if __name__ == "__main__":
  app.run(debug=True)