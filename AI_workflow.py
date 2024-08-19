from langchain.prompts import PromptTemplate
from langchain import LLMChain
from langchain.prompts import PromptTemplate
from transformers import T5Tokenizer, T5ForConditionalGeneration 
from RAG_tool import knowledge_tree_tool

def main():
    """
        The plam is to build a 1-chain LLM workflow that incorporates the knowledge tree-tool to improve 
        information accuracy.
    """
    WorkflowInstance1 = LLMWorkflow()

    # Test the workflow
    question = "What is the capital of France?"
    response = WorkflowInstance1.workflow(question)
    #write response to a file
    with open("response.txt", "w") as f:
        f.write(response)

class LLMWorkflow():
    def __init__(self):
        """
        Initializes the AI_workflow object.

        Parameters:
        - model: The T5 model for conditional generation.
        - tokenizer: The T5 tokenizer.
        - template: The template string for generating prompts.
        - prompt: The prompt template object.
        - tools: The list of tools used in the workflow.
        - LLMChain: The LLMChain object.

        Returns:
        None
        """
        self.model = T5ForConditionalGeneration.from_pretrained("t5-small")
        self.tokenizer = T5Tokenizer.from_pretrained("t5-small")
        self.template = "Answer the following with the most accurate knowledge you have access to: {question}"
        self.prompt = PromptTemplate(template=self.template, input_variables=["question"])
        self.tools = [knowledge_tree_tool]
        self.LLMChain = LLMChain(
            model=self.model,
            tokenizer=self.tokenizer,
            prompt=self.prompt,
            tools=self.tools)
    
    def workflow(self, question : str):
        return self.LLMChain.run(question)

if(__name__ == "__main"):
    main()