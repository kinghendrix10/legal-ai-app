# config.py

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
    NEO4J_URL = os.getenv('NEO4J_URL')
    NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD')
    QDRANT_URL = os.getenv('QDRANT_URL')
    QDRANT_API_KEY = os.getenv('QDRANT_API_KEY')
