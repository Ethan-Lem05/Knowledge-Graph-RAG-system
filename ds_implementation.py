### IMPORTS ###
import torch
from transformers import RobertaModel, RobertaTokenizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import uuid
import sqlite3
import json


class Node:
    def __init__(self, id, text, embedding_value, edges):
        self.id = id
        self.text = text
        self.embedding_value = embedding_value
        self.edges = edges

    def get_id(self):
        return self.id;

    def get_embedding_value(self):
        return self.embedding_value
    
    def get_edges(self):
        return self.edges
    
    def get_text(self):
        return self.text

class knowledge_graph:

    ### CONSTANTS ###

    #Our knowledge graph will be a hashmap with an ID as its key, leading to a value of a list of all connected node IDS and 
    #embedded text that goes along with them

    ### FUNCTIONS ###

    def __init__(self):
        self.SIMILARITY_THRESHOLD = 0.8
        self.graph = []
        #Using roberta for the task of tokenizing input for use in our knowledge graph
        self.TOKENIZER = RobertaTokenizer.from_pretrained('roberta-base')
        self.MODEL = RobertaModel.from_pretrained('roberta-base')
    
    def add_to_ds(self, value):
        #generate ID
        id = str(uuid.uuid4())
        text = value
        #generate embeddings from the value
        tokens = self.TOKENIZER(value, return_tensors='pt')
        with torch.no_grad():
            output = self.MODEL(**tokens)

        embeddings = output.last_hidden_state
        single_vector_value = torch.mean(embeddings) 
        
        #create a node
        node = Node(id, text, single_vector_value, [])

        self.add_edges_to_node(node)

        self.graph.append(node)

    #### Helper function to add edges to a node ####
    def add_edges_to_node(self, node):
        for n in self.graph:
            if node != n and self.compute_similarity(node, n) >= self.SIMILARITY_THRESHOLD:
                node.get_edges().append(n.get_id())
                n.get_edges().append(node.get_id())

    #### Helper function to compute similarity between two nodes ####
    def compute_similarity(self, node1, node2):

        node1_embedding = node1.get_embedding_value().detach().numpy()
        node1_embedding.reshape(1,-1)

        node2_embedding = node2.get_embedding_value().detach().numpy()
        node1_embedding.reshape(1,-1)

        if node1_embedding.shape != node2_embedding.shape:
            raise ValueError(f"Shape mismatch: node1_embedding shape {node1_embedding.shape} and node2_embedding shape {node2_embedding.shape} must be the same.")

        #compute cosine similarity between two nodes
        similarity = cosine_similarity(node1_embedding, node2_embedding)
        return similarity
 
    ###helper function to search for a node by its ID###
    def search_ds_by_id(self, id):
        for node in self.graph:
            if(node.get_id() == id):
                return node

    def search_ds_by_context(self,text):
        similar_nodes = []

        tokens = self.TOKENIZER(text)
        with torch.no_grad():
            output = self.MODEL(tokens)
        
        embeddings = output.last_hidden_state
        single_vector_value = torch.mean(embeddings)

        for node in self.graph:
            if(self.compute_similarity(node.get_embedding_value(),single_vector_value) >= self.SIMILARITY_THRESHOLD):
                similar_nodes.append(node)

        similar_nodes.sort(key = lambda x: self.compute_similarity(x.get_embedding_value(),single_vector_value), reverse = True)
        
        return similar_nodes[0]

    def remove_from_ds(self,id):
        self.graph.remove(self.search_ds_by_id(id))
        for node in self.graph:
            if(id in node.get_edges()):
                node.get_edges().remove(id)

    ### DB functions ###
    def save_graph_to_db(self):
        conn = sqlite3.connect('kg.db')
        cursor = conn.cursor()

        for n in self.graph:
            cursor.execute("INSERT OR IGNORE INTO kg VALUES (?, ?, ?, ?)", 
                           (n.get_id(), n.get_text(), n.get_embedding_value(), json.dumps(n.get_edges()))) 
        
        conn.commit()
        cursor.close()
        conn.close()

    def load_graph_from_db(self):
        conn = sqlite3.connect('kg.db')
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM kg")
        rows = cursor.fetchall()
        
        self.graph = [Node(r.id, r.text, r.embedding, json.loads(r.edges)) for r in rows]

        cursor.close()
        conn.close()

### END ###