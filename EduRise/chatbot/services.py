import requests
from django.conf import settings
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

class RemoteRAGService:
    """
    Service to handle RAG queries by calling the remote Hugging Face Space API.
    This replaces the local FAISS/SentenceTransformer implementation to save memory.
    """
    
    HF_SPACE_URL = getattr(settings, 'HF_SPACE_URL', 'https://yessinehakim-edurise.hf.space')

    def __init__(self):
        self.initialized = True  # Remote service is always "initialized" if URL is set


    def generate_response(self, query: str) -> Dict[str, Any]:
        """
        Send a query to the remote RAG endpoint.
        The HF Space has GROQ_API_KEY configured in its own environment.
        """
        endpoint = f"{self.HF_SPACE_URL}/ask"
        payload = {"query": query}
        
        try:
            # Short timeout to prevent hanging the Django web request
            response = requests.post(endpoint, json=payload, timeout=20.0)
            
            if response.status_code == 500:
                # Try to extract error details from response
                try:
                    error_detail = response.json().get('detail', response.text)
                except:
                    error_detail = response.text
                logger.error(f"Remote RAG API Error 500: {error_detail}")
                return {
                    "response": "The AI assistant encountered an error. This may be due to missing or invalid GROQ_API_KEY on the Hugging Face Space.",
                    "sources": [],
                    "error": error_detail
                }
            elif response.status_code != 200:
                logger.error(f"Remote RAG API Error {response.status_code}: {response.text}")
                return {
                    "response": f"The AI assistant encountered an error ({response.status_code}). Please try again later.",
                    "sources": [],
                    "error": response.text
                }
            
            result = response.json()
            
            # Map API response format to what the Django view expects
            return {
                "response": result.get("answer"),
                "sources": result.get("sources", []),
                "error": None
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Remote RAG API Connection Error: {str(e)}")
            return {
                "response": "The AI assistant is currently unreachable. Please check your internet connection and verify the Hugging Face Space is running.",
                "sources": [],
                "error": str(e)
            }

# Singleton instance access
_rag_service = None

def get_rag_service():
    global _rag_service
    if _rag_service is None:
        _rag_service = RemoteRAGService()
    return _rag_service 
