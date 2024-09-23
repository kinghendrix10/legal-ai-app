import logging
from typing import List, Dict
import json
import re
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.graph_stores.neo4j import Neo4jPropertyGraphStore
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.indices.keyword_table import KeywordTableIndex
from llama_index.embeddings.fastembed import FastEmbedEmbedding
from llama_index.llms.groq import Groq
from llama_index.core import Settings, PropertyGraphIndex
from llama_index.core import PromptTemplate
from llama_index.core.tools import QueryEngineTool
from llama_index.core.query_engine import RouterQueryEngine
from llama_index.core.selectors import LLMSingleSelector, LLMMultiSelector
from llama_index.core.selectors import (
    PydanticMultiSelector,
    PydanticSingleSelector,
)
from llama_index.core.response_synthesizers import TreeSummarize
from dotenv import load_dotenv
import numpy as np
import nest_asyncio
import os

load_dotenv()
nest_asyncio.apply()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class IntegratedKnowledgeBaseQuery:
    def __init__(self):
        self.embed_model, self.llm = self._initialize_components()
        self.graph_store = self._setup_graph_store()
        self.vector_store = self._setup_vector_store()
        self.graph_index, self.vector_index = self._setup_index()

    def _initialize_components(self):
        embed_model = FastEmbedEmbedding(model_name="BAAI/bge-small-en-v1.5")
        Settings.embed_model = embed_model
        llm = Groq(model="llama3-70b-8192", api_key=os.getenv('GROQ_API_KEY'), temperature=0)
        Settings.llm = llm

        return embed_model, llm

    def _setup_graph_store(self):
        return Neo4jPropertyGraphStore(
            url = os.getenv('NEO4J_URL'),
            username = "neo4j",
            password = os.getenv('NEO4J_PASSWORD'),
            database="neo4j",
            refresh_schema=False,
            sanitize_query_output=True
        )

    def get_neo4j_schema(self):
        cypher_query = """
        CALL db.schema.visualization()
        """
        try:
            result = self.graph_store.structured_query(cypher_query)
            return result
        except Exception as e:
            logging.error(f"Error retrieving Neo4j schema: {str(e)}")
            return None

    def _setup_vector_store(self):
        return QdrantVectorStore(
            url=os.getenv("QDRANT_URL"),
            api_key=os.getenv("QDRANT_API_KEY"),
            collection_name="law_docs",
        )

    def _setup_index(self):
        storage_context = StorageContext.from_defaults(
            vector_store=self.vector_store,
            graph_store=self.graph_store,
        )
        graph_index = PropertyGraphIndex.from_existing(
            property_graph_store=self.graph_store,
            storage_context=storage_context)

        vector_index = VectorStoreIndex.from_vector_store(
            vector_store=self.vector_store,
            storage_context=storage_context,
        )
        return graph_index, vector_index

    def diagnose_stores(self):
        logging.info("Diagnosing graph store...")
        self._diagnose_graph_store()
        logging.info("Diagnosing vector store...")
        self._diagnose_vector_store()

    def _diagnose_graph_store(self):
        query = "MATCH (n) RETURN count(n) as node_count"
        result = self.graph_store.structured_query(query)
        node_count = result[0]['node_count']
        logging.info(f"Total nodes in the graph: {node_count}")

        query = "MATCH (n) RETURN DISTINCT labels(n) as node_types"
        result = self.graph_store.structured_query(query)
        node_types = [r['node_types'][0] for r in result if r['node_types']]
        logging.info(f"Node types in the graph: {', '.join(node_types)}")

        query = "MATCH (n) RETURN n LIMIT 5"
        result = self.graph_store.structured_query(query)
        logging.info("Sample nodes:")
        for record in result:
            logging.info(record['n'])

    def _diagnose_vector_store(self):
        collection_info = self.vector_store.client.get_collection(collection_name="law_docs")
        logging.info(f"Vector store collection info: {collection_info}")

    def format_case_details(self, results: List[Dict]) -> str:
        if not results:
            return "No case found with the given ID."

        case = results[0]['c']
        formatted_result = f"Case: {case.get('case_name', 'Unknown')}\n"
        formatted_result += f"Date Filed: {case.get('date_filed', 'Unknown')}\n"
        formatted_result += f"Court: {results[0]['court'].get('short_name', 'Unknown')}\n"
        formatted_result += f"Judges: {', '.join([j['name'] for j in results[0]['judges']])}\n"
        formatted_result += f"Author: {results[0]['author'].get('name', 'Unknown') if results[0]['author'] else 'Unknown'}\n"
        formatted_result += f"Attorneys: {', '.join([a['name'] for a in results[0]['attorneys']])}\n"
        formatted_result += f"Plaintiff: {results[0]['plaintiff'].get('name', 'Unknown') if results[0]['plaintiff'] else 'Unknown'}\n"
        formatted_result += f"Defendant: {results[0]['defendant'].get('name', 'Unknown') if results[0]['defendant'] else 'Unknown'}\n"
        formatted_result += f"Citations: {', '.join([c['text'] for c in results[0]['citations']])}\n"
        formatted_result += f"Opinion Type: {results[0]['opinion'].get('type', 'Unknown') if results[0]['opinion'] else 'Unknown'}\n"
        formatted_result += f"Docket Number: {results[0]['docket'].get('id', 'Unknown') if results[0]['docket'] else 'Unknown'}\n"

        return formatted_result

    def get_case_details(self, case_id):
        cypher_query = """
        MATCH (c:Case {id: $case_id})
        OPTIONAL MATCH (c)-[:DECIDED_BY]->(j:Judge)
        OPTIONAL MATCH (c)-[:AUTHORED_BY]->(a:Judge)
        OPTIONAL MATCH (c)-[:HEARD_IN]->(ct:Court)
        OPTIONAL MATCH (c)-[:REPRESENTED_BY]->(att:Attorney)
        OPTIONAL MATCH (p:Party)-[:FILED_CASE]->(c)
        OPTIONAL MATCH (c)-[:AGAINST]->(d:Party)
        OPTIONAL MATCH (c)-[:CITED_BY_BYCITED_BYit:Citation)
        OPTIONAL MATCH (c)-[:HAS_OPINION]->(o:Opinion)
        OPTIONAL MATCH (c)-[:HAS_DOCKET]->(docket:Docket)
        RETURN c, collect(DISTINCT j) as judges, a as author, ct as court,
               collect(DISTINCT att) as attorneys, p as plaintiff, d as defendant,
               collect(DISTINCT cit) as citations, o as opinion, docket
        """
        results = self.graph_store.structured_query(cypher_query, {"case_id": case_id})
        return results

    def format_graph_results(self, query):
        cypher_query = """
                MATCH (e)
                WHERE e.name CONTAINS $entity_name
                OPTIONAL MATCH (e)-[r]-(related)
                RETURN e as entity, type(r) as relationship_type, related
                LIMIT 10
                """
        # Extract key entities from the query
        entities = re.findall(r'\b[A-Z][a-z]+ (?:[A-Z][a-z]+ )*(?:Co\.|Corporation|Inc\.|LLC)\b|\b[A-Z][a-z]+\b', query)

        graph_results = []
        case_details = []
        for entity in entities:
            results = self.graph_store.structured_query(cypher_query, {"entity_name": entity})
            graph_results.extend(results)
            # Check if any of the results are Case nodes
            for result in results:
                if 'Case' in result['entity'].get('labels', []):
                    case_id = result['entity_id']
                    case_detail = self.get_case_details(case_id)
                    if case_detail:
                        formatted_case = self.format_case_details(case_detail)
                        case_details.append(formatted_case)
        formatted_results = []
        for graph_result in graph_results:
            entity = graph_result.get('entity', {})
            rel_type = graph_result.get('relationship_type')
            related = graph_result.get('related', {})

            entity_name = entity.get('name', 'Unknown')
            entity_type = next(iter(entity.get('labels', [])), 'Unknown')
            formatted_result = f"- {entity_name} ({entity_type})"

            if rel_type and related:
                related_name = related.get('name', 'Unknown')
                related_type = next(iter(related.get('labels', [])), 'Unknown')
                formatted_result += f"\n  {rel_type} {related_name} ({related_type})"

            formatted_results.append(formatted_result)

        return "\n".join(formatted_results), case_details

    def format_vector_results(self, query) -> str:
        query_vector = self.embed_model.get_text_embedding(query)
        vector_results = self.vector_store.client.search(
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

    def generate_llm_response(self, query: str, response: str, graph_results: List[Dict], vector_results: List[Dict], case_details: List[str]) -> str:
        graph_context = graph_results
        vector_context = vector_results

        prompt = f"""You are a highly knowledgeable Legal AI assistant specializing in analyzing court cases and legal precedents. Your task is to provide a very short and accurate response to the following query based on the information data provided.

        Query: {query}

        Data: {response}

        Knowledgebase Context: {graph_context} + {vector_context}

        Case Details: {case_details}

        Instructions:
        1. Analyze the Knowledgebase context, data and specific case details, extracting all relevant information related to the query.
        2. Provide a clear, concise, and well-structured response that directly addresses the query.
        3. Include specific details such as case names, courts, judges, plaintiffs, defendants, attorneys, dates filed, decision dates, case outcomes, judicial opinions and legal principles when available in any of the contexts but do not use the term 'document' or 'context' in your response.
        4. If the contexts contain information about multiple related cases or legal issues, combine and summarize them briefly and explain their relevance to the query.
        5. If there are any conflicting opinions or interpretations in the contexts, present them objectively and explain the implications.
        6. Use legal terminology accurately, but also provide explanations for complex terms to ensure clarity.
        7. If the contexts don't provide sufficient information to fully answer the query, clearly state what is known and what information is missing.
        8. Do not refer to the query, documents and contexts directly in your answer; instead, incorporate the information seamlessly into your response by saying "Based on my knowledge ...".
        9. Do not make assumptions or include information not present in the given contexts.
        10. Conclude your response with a brief summary of the key points.
        11. After your main response, suggest two follow-up questions that would be relevant for further exploration of the topic, prefaced with "For further exploration, you might consider asking:".

        Remember to maintain an objective, professional tone throughout your response. Do not refer to the query or contexts directly in your answer; instead, incorporate the information seamlessly into your response.

        Now, based on these instructions, please provide your comprehensive analysis and response."""

        llm_output = self.llm.complete(prompt).text
        return llm_output

    def query_knowledge_base(self, query: str) -> str:
        logging.info(f"Querying knowledge base: {query}")
        # try:
        # Create query engines
        graph_query_engine = self.graph_index.as_query_engine()
        vector_query_engine = self.vector_index.as_query_engine()

        # Create tools
        graph_tool = QueryEngineTool.from_defaults(
            query_engine=graph_query_engine,
            description="Useful for answering questions about relationships and connections between legal entities, cases, and concepts",
        )

        vector_tool = QueryEngineTool.from_defaults(
            query_engine=vector_query_engine,
            description="Useful for answering detailed questions about legal content, precedents, and case details",
        )

        TREE_SUMMARIZE_PROMPT_TMPL = (
            """You are a helpful legal AI assistant specialized in understanding the legal enquiries"""
        )
        tree_summarize = TreeSummarize(
            summary_template=PromptTemplate(TREE_SUMMARIZE_PROMPT_TMPL)
        )

        # Create router query engine
        router_query_engine = RouterQueryEngine(
            selector=LLMMultiSelector.from_defaults(),
            query_engine_tools=[graph_tool, vector_tool],
            summarizer=tree_summarize,
        )

        # Execute query
        response = router_query_engine.query(query)

        graph_results, case_details = self.format_graph_results(query)
        logging.info (f"Formatted graph results: {graph_results}")

        vector_results = self.format_vector_results(query)
        logging.info (f"Formatted vector results: {vector_results}")

        llm_response = self.generate_llm_response(query, str(response), graph_results, vector_results, case_details)
        logging.info(f"LLM response: {llm_response}")

        return str(llm_response)
    
def main():
    kb_query = IntegratedKnowledgeBaseQuery()
    kb_query.diagnose_stores()

    while True:
        print("\n--- Legal AI Knowledge Base ---")
        query = input("\nEnter your query (or 'quit' to exit): ")
        if query.lower() == 'quit':
            break
        response = kb_query.query_knowledge_base(query)
        print(response)
        print("\n" + "=" * 10 + "\n")

if __name__ == "__main__":
    main()
