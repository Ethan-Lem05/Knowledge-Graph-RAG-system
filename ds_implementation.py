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
        """
        Initializes an instance of the class.

        Args:
            id (int): The ID of the instance.
            text (str): The text associated with the instance.
            embedding_value (float): The embedding value of the instance.
            edges (list): The list of edges associated with the instance.

        Returns:
            None
        """
        self.id = id
        self.text = text
        self.embedding_value = embedding_value
        self.edges = edges

    def get_id(self):
        """
        Returns the id of the object.

        Returns:
            int: The id of the object.
        """
        return self.id

    def get_embedding_value(self):
        """
        Returns the embedding value.

        Returns:
            The embedding value.
        """
        return self.embedding_value
    
    def get_edges(self):
        """
        Returns the edges of the node.

        Returns:
            list: A list of edges in the node.
        """
        return self.edges
    
    def get_text(self):
        """
        Returns the text attribute of the object.

        Returns:
            str: The text attribute of the object.
        """
        return self.text

class knowledge_graph:

    ### CONSTANTS ###

    # Our knowledge graph will be a hashmap with an ID as its key, leading to a value of a list of all connected node IDS and 
    # embedded text that goes along with them

    ### FUNCTIONS ###

    def __init__(self):
        """
        Initializes the object.

        Parameters:
        - SIMILARITY_THRESHOLD (float): The similarity threshold used for comparing nodes in the knowledge graph.
        - graph (list): The knowledge graph.
        - TOKENIZER (RobertaTokenizer): The tokenizer used for tokenizing input.
        - MODEL (RobertaModel): The model used for processing input.

        Returns:
        None
        """
        self.SIMILARITY_THRESHOLD = 0.5
        self.graph = []
        # Using roberta for the task of tokenizing input for use in our knowledge graph
        self.TOKENIZER = RobertaTokenizer.from_pretrained('roberta-base')
        self.MODEL = RobertaModel.from_pretrained('roberta-base')
    
    def add_to_ds(self, value):
        """
        Adds a node to the data structure.
        Parameters:
            value (str): The value to be added.
        Returns:
            None
        """
        # Generate ID
        id = str(uuid.uuid4())
        text = value
        # Generate embeddings from the value
        tokens = self.TOKENIZER(value, return_tensors='pt')
        with torch.no_grad():
            output = self.MODEL(**tokens)

        embeddings = output.last_hidden_state
        single_vector_value = torch.mean(embeddings, dim=1)  # Corrected to take mean along the correct dimension
        
        # Create a node
        node = Node(id, text, single_vector_value, [])

        self.add_edges_to_node(node)
        self.graph.append(node)

    #### Helper function to add edges to a node ####
    def add_edges_to_node(self, node):
        """
        Adds edges to a given node based on similarity threshold.

        Parameters:
            node (Node): The node to which edges will be added.

        Returns:
            None
        """
        for n in self.graph:
            if node != n and self.compute_similarity(node, n) >= self.SIMILARITY_THRESHOLD:
                node.get_edges().append(n.get_id())
                n.get_edges().append(node.get_id())

    #### Helper function to compute similarity between two nodes ####
    def compute_similarity(self, node1, node2):
        """
        Compute the cosine similarity between two nodes.
        Parameters:
        - node1: The first node.
        - node2: The second node.
        Returns:
        - similarity: The cosine similarity between the two nodes.
        """
        node1_embedding = node1.get_embedding_value().detach().numpy().reshape(1, -1)
        #print(node1_embedding.shape)

        node2_embedding = node2.get_embedding_value().detach().numpy().reshape(1, -1)
        #print(node2_embedding.shape)

        if node1_embedding.shape != node2_embedding.shape:
            raise ValueError(f"Shape mismatch: node1_embedding shape {node1_embedding.shape} and node2_embedding shape {node2_embedding.shape} must be the same.")

        # Compute cosine similarity between two nodes
        similarity = cosine_similarity(node1_embedding, node2_embedding)
        print(similarity)
        return similarity[0][0]  # Return the scalar similarity value

    ### Helper function to search for a node by its ID ###
    def search_ds_by_id(self, id):
        """
        Searches for a node in the graph by its ID.

        Parameters:
            id (int): The ID of the node to search for.

        Returns:
            Node: The node with the specified ID, or None if not found.
        """
        for node in self.graph:
            if node.get_id() == id:
                return node

    def search_ds_by_context(self, text):
        """
        Searches for similar nodes in the graph based on the given text context.
        Args:
            text (str): The text context to search for.
        Returns:
            list: A list of similar nodes found in the graph, sorted by similarity score in descending order. Returns an empty list if no similar nodes are found.
        """
        similar_nodes = []

        tokens = self.TOKENIZER(text, return_tensors='pt')
        with torch.no_grad():
            output = self.MODEL(**tokens)
        
        embeddings = output.last_hidden_state
        single_vector_value = torch.mean(embeddings, dim=1)

        for node in self.graph:
            if self.compute_similarity(node, Node(None, None, single_vector_value, [])) >= self.SIMILARITY_THRESHOLD:
                similar_nodes.append(node)

        similar_nodes.sort(key=lambda x: self.compute_similarity(x, Node(None, None, single_vector_value, [])), reverse=True)
        
        return similar_nodes[0:1] if similar_nodes else []

    def remove_from_ds(self, id):
        """
        Removes a node with the given ID from the data structure.

        Parameters:
            id (int): The ID of the node to be removed.

        Returns:
            None
        """
        self.graph.remove(self.search_ds_by_id(id))
        for node in self.graph:
            if id in node.get_edges():
                node.get_edges().remove(id)

    ### DB functions ###
    def save_graph_to_db(self):
        """
        Saves the graph to a SQLite database.
        Raises:
            sqlite3.OperationalError: If there is an error saving the graph.
        """
        try:
            conn = sqlite3.connect('kg.db')
            cursor = conn.cursor()

            for n in self.graph:
                cursor.execute("INSERT OR IGNORE INTO kg VALUES (?, ?, ?, ?)", 
                            (n.get_id(), n.get_text(), n.get_embedding_value().tolist(), json.dumps(n.get_edges()))) 
            
            conn.commit()
            cursor.close()
            conn.close()
        except sqlite3.OperationalError as e:
            print(f"Error saving graph: {e}")

    def load_graph_from_db(self):
        """
        Loads the graph data from the SQLite database.
        Returns:
            None
        Raises:
            sqlite3.Error: If there is an error while executing the SQL query or fetching the data.
        """
        try:
            conn = sqlite3.connect('kg.db')
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM kg")
            rows = cursor.fetchall()
            
            self.graph = [Node(r[0], r[1], torch.tensor(json.loads(r[2])), json.loads(r[3])) for r in rows]

            cursor.close()
            conn.close()
        except sqlite3.Error as e:
            print(f"SQLite3 error: {e}")

### END ###