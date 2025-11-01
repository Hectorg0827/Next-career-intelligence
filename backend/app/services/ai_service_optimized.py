"""
AI Service Wrapper with Retry Logic and Circuit Breaker
Optimizes Gemini AI API calls for reliability and performance
"""

import asyncio
from typing import Optional, Any, Callable
from functools import wraps
from datetime import datetime, timedelta
from loguru import logger
import google.generativeai as genai

from app.core.config import settings
from app.core.cache import cache_response, get_cached_ai_response, cache_ai_response

# Configure Gemini
genai.configure(api_key=settings.GEMINI_API_KEY)


class CircuitBreaker:
    """
    Circuit breaker pattern implementation
    Prevents cascading failures when AI service is down
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: int = 60,
        expected_exception: type = Exception
    ):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def call(self, func: Callable, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        
        if self.state == "OPEN":
            if datetime.now() - self.last_failure_time > timedelta(seconds=self.timeout):
                self.state = "HALF_OPEN"
                logger.info("Circuit breaker entering HALF_OPEN state")
            else:
                raise Exception("Circuit breaker is OPEN - service temporarily unavailable")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise e
    
    def _on_success(self):
        """Reset circuit breaker on successful call"""
        self.failure_count = 0
        if self.state == "HALF_OPEN":
            self.state = "CLOSED"
            logger.info("Circuit breaker back to CLOSED state")
    
    def _on_failure(self):
        """Handle failure and potentially open circuit"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            logger.error(
                f"Circuit breaker OPEN after {self.failure_count} failures. "
                f"Will retry after {self.timeout} seconds."
            )


# Global circuit breaker for AI service
ai_circuit_breaker = CircuitBreaker(
    failure_threshold=3,
    timeout=30,
    expected_exception=Exception
)


async def retry_with_backoff(
    func: Callable,
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    max_delay: float = 30.0
):
    """
    Retry function with exponential backoff
    
    Args:
        func: Async function to retry
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay between retries (seconds)
        backoff_factor: Multiplier for delay on each retry
        max_delay: Maximum delay between retries (seconds)
    
    Returns:
        Function result
    """
    delay = initial_delay
    last_exception = None
    
    for attempt in range(max_retries + 1):
        try:
            return await func()
        except Exception as e:
            last_exception = e
            
            if attempt < max_retries:
                logger.warning(
                    f"Attempt {attempt + 1}/{max_retries + 1} failed: {e}. "
                    f"Retrying in {delay:.1f}s..."
                )
                await asyncio.sleep(delay)
                delay = min(delay * backoff_factor, max_delay)
            else:
                logger.error(f"All {max_retries + 1} attempts failed: {e}")
    
    raise last_exception


class GeminiAIService:
    """
    Optimized Gemini AI service with caching, retry logic, and circuit breaker
    """
    
    def __init__(self):
        model_name = getattr(settings, 'GEMINI_MODEL', 'gemini-1.5-flash')
        self.model = genai.GenerativeModel(model_name)
        self.timeout = 30  # seconds
    
    async def generate_content(
        self,
        prompt: str,
        use_cache: bool = True,
        cache_ttl: int = 3600,
        max_retries: int = 3
    ) -> str:
        """
        Generate content with Gemini AI
        
        Args:
            prompt: Input prompt
            use_cache: Whether to use cached responses
            cache_ttl: Cache time-to-live in seconds
            max_retries: Maximum retry attempts
        
        Returns:
            Generated text response
        """
        
        # Check cache first
        if use_cache:
            cached_response = await get_cached_ai_response(prompt)
            if cached_response:
                logger.info(f"AI response cache HIT for prompt: {prompt[:50]}...")
                return cached_response
        
        # Generate new response with retry logic
        async def _generate():
            try:
                # Use circuit breaker
                response = ai_circuit_breaker.call(
                    self.model.generate_content,
                    prompt
                )
                
                text = response.text
                
                # Cache the response
                if use_cache and text:
                    await cache_ai_response(prompt, text, cache_ttl)
                
                return text
                
            except Exception as e:
                logger.error(f"AI generation failed: {e}")
                raise
        
        return await retry_with_backoff(_generate, max_retries=max_retries)
    
    async def generate_with_timeout(
        self,
        prompt: str,
        timeout: Optional[int] = None
    ) -> str:
        """
        Generate content with timeout
        
        Args:
            prompt: Input prompt
            timeout: Timeout in seconds (uses default if not specified)
        
        Returns:
            Generated text response
        """
        timeout = timeout or self.timeout
        
        try:
            return await asyncio.wait_for(
                self.generate_content(prompt),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            logger.error(f"AI generation timed out after {timeout}s")
            raise TimeoutError(f"AI request timed out after {timeout} seconds")
    
    async def batch_generate(
        self,
        prompts: list[str],
        max_concurrent: int = 5
    ) -> list[str]:
        """
        Generate multiple responses concurrently
        
        Args:
            prompts: List of prompts
            max_concurrent: Maximum concurrent requests
        
        Returns:
            List of generated responses
        """
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def _generate_with_semaphore(prompt: str):
            async with semaphore:
                return await self.generate_content(prompt)
        
        tasks = [_generate_with_semaphore(prompt) for prompt in prompts]
        return await asyncio.gather(*tasks, return_exceptions=True)
    
    def get_circuit_breaker_status(self) -> dict:
        """Get current circuit breaker status"""
        return {
            "state": ai_circuit_breaker.state,
            "failure_count": ai_circuit_breaker.failure_count,
            "last_failure": ai_circuit_breaker.last_failure_time.isoformat() if ai_circuit_breaker.last_failure_time else None
        }


# Global AI service instance
ai_service = GeminiAIService()


def get_ai_service() -> GeminiAIService:
    """Get AI service instance"""
    return ai_service


# Decorator for AI-powered endpoints
def with_ai_optimization(
    use_cache: bool = True,
    cache_ttl: int = 3600,
    max_retries: int = 3,
    timeout: int = 30
):
    """
    Decorator to optimize AI-powered endpoint with caching and retry logic
    
    Usage:
        @router.post("/analyze")
        @with_ai_optimization(use_cache=True, cache_ttl=1800)
        async def analyze_career(request: CareerAnalysisRequest):
            response = await ai_service.generate_content(request.prompt)
            return {"analysis": response}
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                logger.error(f"AI endpoint error: {e}")
                raise
        
        return wrapper
    return decorator


# Monitoring functions

async def get_ai_service_stats() -> dict:
    """Get AI service statistics"""
    return {
        "circuit_breaker": ai_service.get_circuit_breaker_status(),
        "status": "operational" if ai_circuit_breaker.state == "CLOSED" else "degraded",
        "api_key_configured": bool(settings.GEMINI_API_KEY)
    }
