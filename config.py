# config.py

import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
    NEO4J_URL = os.environ.get('NEO4J_URL')
    NEO4J_PASSWORD = os.environ.get('NEO4J_PASSWORD')
    QDRANT_URL = os.environ.get('QDRANT_URL')
    QDRANT_API_KEY = os.environ.get('QDRANT_API_KEY')
