"""
Request/Response Compression Middleware
Reduces bandwidth and improves response times
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import gzip
import json
from loguru import logger


class CompressionMiddleware(BaseHTTPMiddleware):
    """
    Middleware to compress API responses
    Automatically compresses responses larger than 1KB with gzip
    """
    
    def __init__(self, app, minimum_size: int = 1024):
        """
        Initialize compression middleware
        
        Args:
            app: FastAPI application
            minimum_size: Minimum response size in bytes to compress (default 1KB)
        """
        super().__init__(app)
        self.minimum_size = minimum_size
    
    async def dispatch(self, request: Request, call_next):
        """Process request and compress response if needed"""
        
        # Process the request
        response = await call_next(request)
        
        # Check if client accepts gzip encoding
        accept_encoding = request.headers.get("accept-encoding", "")
        if "gzip" not in accept_encoding.lower():
            return response
        
        # Only compress successful responses
        if response.status_code >= 400:
            return response
        
        # Get response body
        response_body = b""
        async for chunk in response.body_iterator:
            response_body += chunk
        
        # Check if response is large enough to compress
        if len(response_body) < self.minimum_size:
            return Response(
                content=response_body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type
            )
        
        # Compress the response
        try:
            compressed_body = gzip.compress(response_body, compresslevel=6)
            
            # Only use compression if it actually reduces size
            if len(compressed_body) < len(response_body):
                compression_ratio = (1 - len(compressed_body) / len(response_body)) * 100
                
                logger.debug(
                    f"Compressed response: {len(response_body)} → {len(compressed_body)} bytes "
                    f"({compression_ratio:.1f}% reduction)"
                )
                
                headers = dict(response.headers)
                headers["Content-Encoding"] = "gzip"
                headers["Content-Length"] = str(len(compressed_body))
                
                return Response(
                    content=compressed_body,
                    status_code=response.status_code,
                    headers=headers,
                    media_type=response.media_type
                )
        except Exception as e:
            logger.warning(f"Compression failed: {e}")
        
        # Return uncompressed response if compression fails or doesn't help
        return Response(
            content=response_body,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.media_type
        )


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware to limit request body size
    Prevents DoS attacks with large payloads
    """
    
    def __init__(self, app, max_size: int = 10 * 1024 * 1024):  # 10MB default
        """
        Initialize request size limit middleware
        
        Args:
            app: FastAPI application
            max_size: Maximum request size in bytes
        """
        super().__init__(app)
        self.max_size = max_size
    
    async def dispatch(self, request: Request, call_next):
        """Check request size before processing"""
        
        # Check Content-Length header
        content_length = request.headers.get("content-length")
        
        if content_length:
            if int(content_length) > self.max_size:
                logger.warning(
                    f"Request rejected: size {content_length} bytes exceeds limit {self.max_size} bytes"
                )
                return Response(
                    content=json.dumps({
                        "error": "request_too_large",
                        "message": f"Request body too large. Maximum size: {self.max_size / (1024*1024):.1f}MB",
                        "max_size_bytes": self.max_size
                    }),
                    status_code=413,
                    media_type="application/json"
                )
        
        return await call_next(request)


def get_compression_stats(original_size: int, compressed_size: int) -> dict:
    """
    Calculate compression statistics
    
    Args:
        original_size: Original size in bytes
        compressed_size: Compressed size in bytes
    
    Returns:
        Dictionary with compression stats
    """
    if original_size == 0:
        return {
            "original_size": 0,
            "compressed_size": 0,
            "ratio": 0,
            "savings_percent": 0
        }
    
    ratio = compressed_size / original_size
    savings = (1 - ratio) * 100
    
    return {
        "original_size": original_size,
        "compressed_size": compressed_size,
        "ratio": round(ratio, 3),
        "savings_percent": round(savings, 2)
    }
