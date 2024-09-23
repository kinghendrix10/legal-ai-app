# Legal AI Knowledge Base

## Overview

The Legal AI Knowledge Base is a Flask application integrated with SocketIO that provides a powerful knowledge base query system using Neo4j and Qdrant. The application allows users to query legal information and receive detailed responses based on the integrated knowledge base.

## Configuration

The application uses environment variables to manage configuration settings. Create a `.env` file in the root directory of the project and add the following environment variables:

```
SECRET_KEY=your_secret_key
GROQ_API_KEY=your_groq_api_key
NEO4J_URL=your_neo4j_url
NEO4J_PASSWORD=your_neo4j_password
QDRANT_URL=your_qdrant_url
QDRANT_API_KEY=your_qdrant_api_key
```

## Installation

To set up the environment and install dependencies, follow these steps:

1. Clone the repository:
   ```bash
   git clone https://github.com/kinghendrix10/legal-ai-app.git
   cd legal-ai-app
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   
## Usage

To run the application and interact with it, follow these steps:

1. Configure the environment variables as described in the "Configuration" section.

2. Start the Flask application:
   ```bash
   python run.py
   ```

3. Open your web browser and navigate to `http://localhost:5000` to access the application.

## Main Components

### Knowledge Base Query System

The knowledge base query system is implemented using Neo4j and Qdrant. It allows users to query legal information and receive detailed responses based on the integrated knowledge base. The main implementation can be found in `app/knowledge_base/integrated_kb_query.py`.

### Web Interface

The web interface is built using Flask and SocketIO. It provides a user-friendly interface for interacting with the knowledge base. The main components of the web interface include:

- `app/templates/base.html`: The base HTML template for the application.
- `app/templates/index.html`: The main HTML template for the application.
- `app/static/css/style.css`: The CSS file for styling the application.
- `app/static/js/main.js`: The JavaScript file for handling user interactions.

## Contributing

Contributions are welcome! If you would like to contribute to the project, please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Make your changes and commit them with descriptive commit messages.
4. Push your changes to your forked repository.
5. Create a pull request to the main repository.

## Dependencies

The project relies on the following dependencies, as listed in `requirements.txt`:

- Flask
- Flask-SocketIO
- llama-index
- fastembed
- groq
- numpy
- neo4j
- qdrant-client
- python-dotenv
- llama-index-graph-stores-neo4j
- llama-parse
- llama-index-vector-stores-qdrant
- llama-index-embeddings-fastembed
- llama-index-llms-groq
- matplotlib
