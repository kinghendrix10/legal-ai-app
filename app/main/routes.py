# app/main/routes.py

from flask import render_template, request, jsonify
from . import main
from ..knowledge_base.integrated_kb_query import IntegratedKnowledgeBaseQuery

kb_query = IntegratedKnowledgeBaseQuery()

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/query', methods=['POST'])
def query():
    query_text = request.json['query']
    response = kb_query.query_knowledge_base(query_text)
    return jsonify({'response': response})
