# app/main/events.py

from app import socketio
from app.knowledge_base.integrated_kb_query import IntegratedKnowledgeBaseQuery

kb_query = IntegratedKnowledgeBaseQuery()

@socketio.on('query')
def handle_query(data):
    query_text = data['query']
    response = kb_query.query_knowledge_base(query_text)
    socketio.emit('response', {'response': response})