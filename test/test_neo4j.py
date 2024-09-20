from llama_index.graph_stores.neo4j import Neo4jPropertyGraphStore
from dotenv import load_dotenv
import os
import re

load_dotenv()

query = 'Marvin Gerber v. Henry Herskovitz'

cypher_query = """
        MATCH (e)
        WHERE e.name CONTAINS $entity_name
        OPTIONAL MATCH (e)-[r]-(related)
        RETURN e as entity, type(r) as relationship_type, related
        LIMIT 10
        """

graph_store = Neo4jPropertyGraphStore(
            url = os.getenv('NEO4J_URL'),
            username = "neo4j",
            password = os.getenv('NEO4J_PASSWORD'),
            refresh_schema=False,
            sanitize_query_output=True
        )
# Extract key entities from the query
entities = re.findall(r'\b[A-Z][a-z]+ (?:[A-Z][a-z]+ )*(?:Co\.|Corporation|Inc\.|LLC)\b|\b[A-Z][a-z]+\b', query)

graph_results = []
for entity in entities:
    results = graph_store.structured_query(cypher_query, {"entity_name": entity})
    graph_results.extend(results)

print (graph_results)