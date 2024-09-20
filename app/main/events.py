# app/main/events.py

from flask_socketio import emit
from .. import socketio
from ..knowledge_base.integrated_kb_query import IntegratedKnowledgeBaseQuery

kb_query = IntegratedKnowledgeBaseQuery()

@socketio.on('query')
def handle_query(data):
    query_text = data['query']
    response = kb_query.query_knowledge_base(query_text)
    emit('response', {'response': response})
