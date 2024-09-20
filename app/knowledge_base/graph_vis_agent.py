# app/knowledge_base/graph_vis_agent.py

import networkx as nx
import matplotlib.pyplot as plt

class GraphVisAgent:
    
    def generate_graph(self, extraction, kb_output):
        G = nx.Graph()

        # Example of adding nodes and edges based on extraction and kb_output
        G.add_node("Entity1", color='red')
        G.add_node("Entity2", color='blue')
        G.add_edge("Entity1", "Entity2", label='related')

        pos = nx.spring_layout(G)
        edge_labels = nx.get_edge_attributes(G, 'label')
        
        plt.figure(figsize=(8, 6))
        nx.draw(G, pos, with_labels=True, node_color=[G.nodes[n]['color'] for n in G.nodes])
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
        
        plt.savefig('app/static/images/legal_graph.png')