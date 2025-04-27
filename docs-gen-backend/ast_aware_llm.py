from typing import Dict, Any
import json
from openai import OpenAI

class ASTAwareLLM:
    def __init__(self, ast_graph, llm_client=None):
        self.ast = ast_graph
        self.llm = llm_client or OpenAI()
        self.conversation_history = []

    def _get_ast_context(self):
        """Convert relevant parts of AST to text for LLM context."""
        return self.ast.to_text()
    
    def query(self, user_input, model="gpt-4"):

        ast_context = self._get_ast_context()

        ## integrate graphRAG formatted prompt here
        system_prompt = f"""
            
        """