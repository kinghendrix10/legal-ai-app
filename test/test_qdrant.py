from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.embeddings.fastembed import FastEmbedEmbedding
from llama_index.llms.groq import Groq
import json
from qdrant_client import QdrantClient
from llama_index.core import Settings
import os
from dotenv import load_dotenv

load_dotenv()

embed_model = FastEmbedEmbedding(model_name="BAAI/bge-small-en-v1.5")
Settings.embed_model = embed_model
llm = Groq(model="llama3-70b-8192", api_key=os.getenv('GROQ_API_KEY'))
Settings.llm = llm

query = 'Marvin Gerber v. Henry Herskovitz'

qdrant_client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY"),
)

vector_store = QdrantVectorStore(
    client=qdrant_client,
    collection_name="law_docs",
)

def format_vector_results(query) -> str:
    query_vector = embed_model.get_text_embedding(query)
    vector_results = qdrant_client.search(
        collection_name="law_docs",
        query_vector=query_vector,
        limit=3
    )
    formatted_results = []
    for i, result in enumerate(vector_results, 1):
        # Access the payload and score attributes directly
        payload = result.payload
        score = result.score
        # Assuming 'content' is a field in your payload
        node_content = json.loads(result.payload['_node_content'])
        content = node_content.get('text', '')
        formatted_results.append(f"Document {i} (Score: {score:.4f}):\n{content[:300]}...")
    return "\n".join(formatted_results)

print(format_vector_results(query))