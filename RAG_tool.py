import requests
from langchain.tools import BaseTool
from langchain.pydantic_v1 import BaseModel, Field

# Define the input schema for the tool
class knowledge_tree_args(BaseModel):
    text: str = Field(
        description="""
            The text to be added to the knowledge tree for future reference, 
            as well as used as a query to find similar documents.
        """)

# Define the tool itself
class knowledge_tree_tool(BaseTool):
    # Define the tool's metadata
    name = "KnowledgeTreeQueryTool"
    description = """
        Queries a knowledge tree for the most similar documents that have been added to your database in the past.
        You should use this tool in order to answer all questions that require accurate information. 
    """
    args_schema = knowledge_tree_args

    def __init__(self):
        """
        Initializes the RAG_tool class.

        Parameters:
        None

        Returns:
        None
        """
        super.__init__()
        self.API_URL = 'http://localhost:5000'
        self.add_node_endpoint = self.API_URL + '/add_node'
        self.similarity_search_endpoint = self.API_URL + '/similarity_search'

    def _run(self, text: str):
        """
        Runs the process of adding the given text to the knowledge tree and querying for similar documents.
        Parameters:
        - text (str): The text to be added to the knowledge tree and used for similarity search.
        Returns:
        - dict: A dictionary containing the response from the knowledge tree API. If an error occurs, the dictionary will contain an "error" key with the corresponding error message.
        """
        try:
            # Add the text to the knowledge tree
            response = requests.post(self.add_node_endpoint, json={'text': text})
            if response.status_code != 200:
                return {"error": f"Error adding node to knowledge tree: {e}"}
        except requests.exceptions.RequestException as e:
            return {"error": f"Error adding node to knowledge tree: {e}"}
        
        try:
            # Query the knowledge tree for similar documents
            response = requests.post(self.similarity_search_endpoint, json={'text': text})
            if response.status_code != 200:
                return {"error": "Error querying knowledge tree."}
        except requests.exceptions.RequestException as e:
            return {"error": f"Error querying data from knowledge tree: {e}"}
        
        return response.json()[0]
    
    async def _arun(self, text: str):
        # No need for async implementation
        raise NotImplementedError("custom_search does not support async")