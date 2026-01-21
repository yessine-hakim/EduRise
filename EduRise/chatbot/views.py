"""
RAG Chatbot Views

Handles chatbot API endpoints for the RAG-powered food environment analysis.
Now configured for Remote Inference via Hugging Face Spaces.
"""

import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .services import get_rag_service

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["POST"])
def chat_api(request):
    """
    API endpoint for chatbot queries.
    Proxies requests to the Remote HF Space.
    """
    try:
        data = json.loads(request.body)
        query = data.get('query', '').strip()
        
        if not query:
            return JsonResponse({
                'error': 'Query is required',
                'response': None,
                'sources': []
            }, status=400)
        
        # Get RAG service
        rag_service = get_rag_service()
        
        # Generate response (calls remote API)
        result = rag_service.generate_response(query)
        
        return JsonResponse({
            'response': result.get('response', ''),
            'sources': result.get('sources', []),
            'error': result.get('error')
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'error': 'Invalid JSON in request body',
            'response': None,
            'sources': []
        }, status=400)
    
    except Exception as e:
        logger.error(f"Error in chat_api: {e}", exc_info=True)
        return JsonResponse({
            'error': f'Internal server error: {str(e)}',
            'response': None,
            'sources': []
        }, status=500)


@require_http_methods(["GET"])
def health_check(request):
    """
    Health check endpoint for RAG service.
    """
    return JsonResponse({
        'status': 'ok',
        'initialized': True,
        'message': 'Remote RAG service is enabled'
    })
 
