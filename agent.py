import os
from dotenv import load_dotenv
from typing import Dict, Any

from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langchain_community.vectorstores import Chroma

# Load environment variables
load_dotenv()

# Search tool
@tool
def search_products(query: str) -> str:
    """
    Search for products in the catalog that match the query.
    This tool should be used when you need to find information about specific products.
    """
    # This function is a placeholder - it will be replaced with the actual vector store search
    # when the agent is created
    return "No products found."

def create_products_agent(vector_store: Chroma):
    """Create a Products Agent that uses the vector store to search for products"""
    
    # Create the LLM
    llm = ChatOpenAI(
        model="gpt-4",
        temperature=0
    )
    
    # Override the search_products tool with a real implementation using the vector store
    def search_product_docs(query: str) -> str:
        """Search for products in the catalog that match the query."""
        docs = vector_store.similarity_search(query, k=5)
        if not docs:
            return "No matching products found in the catalog."
        
        results = []
        for i, doc in enumerate(docs, 1):
            source = doc.metadata.get("source", "Unknown source")
            content = doc.page_content.strip()
            results.append(f"Result {i} (from {source}):\n{content}\n")
        
        return "\n".join(results)
    
    # Update the search_products tool with the real implementation
    search_products.func = search_product_docs
    
    # Define tools
    tools = [search_products]
    
    # Create a system prompt
    system_prompt = """You are the 'Products Agent', an AI assistant specialized in helping customers find information about products from the shop catalog.

Your goal is to provide accurate information about products based on the catalog data. When users ask questions, use the search_products tool to find relevant product information.

Follow these guidelines:
1. Always search for relevant information in the catalog when asked about products.
2. If you don't find the information, politely say you don't have that information in the catalog.
3. Be concise and helpful in your responses.
4. If a user asks something unrelated to the product catalog, politely redirect them.
5. Don't make up information about products that's not in the catalog.

Use the tools available to you to provide the most helpful response.
"""
    
    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content=system_prompt),
        MessagesPlaceholder(variable_name="chat_history", optional=True),
        HumanMessage(content="{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    
    # Create the agent
    agent = create_openai_functions_agent(llm, tools, prompt)
    
    # Create the agent executor
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
    )
    
    return agent_executor 