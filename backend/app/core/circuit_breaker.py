"""
Circuit Breaker Pattern Implementation
Prevents cascading failures when external services are down

States:
- CLOSED: Normal operation, requests pass through
- OPEN: Service is down, requests fail immediately
- HALF_OPEN: Testing if service recovered

Use cases:
- Gemini AI API calls
- SendGrid email API
- Stripe payment API
- External job board APIs
"""

from enum import Enum
from datetime import datetime, timedelta
from typing import Callable, Any, Optional
from loguru import logger
import asyncio
from functools import wraps


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Service down, fail fast
    HALF_OPEN = "half_open"  # Testing recovery


class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open"""
    pass


class CircuitBreaker:
    """
    Circuit breaker for external service calls

    Usage:
        cb = CircuitBreaker(
            name="gemini_api",
            failure_threshold=5,  # Open after 5 failures
            recovery_timeout=60,  # Try recovery after 60 seconds
            expected_exception=httpx.HTTPError
        )

        try:
            result = await cb.call(gemini_api_function, *args)
        except CircuitBreakerOpenError:
            # Fallback logic
            return cached_result
    """

    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: type = Exception,
        success_threshold: int = 2  # Successes needed to close from half-open
    ):
        """
        Initialize circuit breaker

        Args:
            name: Service name for logging
            failure_threshold: Number of failures before opening
            recovery_timeout: Seconds to wait before trying again
            expected_exception: Exception type that counts as failure
            success_threshold: Successes needed in half-open to close
        """
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.success_threshold = success_threshold

        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = CircuitState.CLOSED

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to try recovery"""
        if self.state == CircuitState.OPEN and self.last_failure_time:
            elapsed = (datetime.now() - self.last_failure_time).total_seconds()
            return elapsed >= self.recovery_timeout
        return False

    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection

        Args:
            func: Async function to call
            *args, **kwargs: Arguments to pass to function

        Returns:
            Function result

        Raises:
            CircuitBreakerOpenError: If circuit is open
            Exception: Original exception if circuit closed
        """
        # Check if circuit should transition to half-open
        if self._should_attempt_reset():
            logger.info(f"🔄 Circuit breaker '{self.name}': OPEN → HALF_OPEN (testing recovery)")
            self.state = CircuitState.HALF_OPEN
            self.success_count = 0

        # If circuit open, fail immediately
        if self.state == CircuitState.OPEN:
            logger.warning(f"⚠️ Circuit breaker '{self.name}': Request blocked (circuit OPEN)")
            raise CircuitBreakerOpenError(
                f"Service '{self.name}' is currently unavailable. "
                f"Circuit breaker is open. Try again in {self.recovery_timeout}s."
            )

        try:
            # Attempt call
            result = await func(*args, **kwargs)

            # Success! Record it
            self._on_success()
            return result

        except self.expected_exception as e:
            # Expected failure, record it
            self._on_failure()
            logger.error(f"❌ Circuit breaker '{self.name}': Call failed - {e}")
            raise
        except Exception as e:
            # Unexpected exception, don't count as failure
            logger.error(f"❌ Circuit breaker '{self.name}': Unexpected error - {e}")
            raise

    def _on_success(self):
        """Handle successful call"""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            logger.info(f"✅ Circuit breaker '{self.name}': Success in HALF_OPEN ({self.success_count}/{self.success_threshold})")

            if self.success_count >= self.success_threshold:
                # Enough successes, close the circuit
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                logger.info(f"✅ Circuit breaker '{self.name}': HALF_OPEN → CLOSED (service recovered)")
        elif self.state == CircuitState.CLOSED:
            # Reset failure count on success
            self.failure_count = 0

    def _on_failure(self):
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()

        if self.state == CircuitState.HALF_OPEN:
            # Failed during recovery test, reopen circuit
            self.state = CircuitState.OPEN
            logger.warning(f"⚠️ Circuit breaker '{self.name}': HALF_OPEN → OPEN (recovery failed)")

        elif self.state == CircuitState.CLOSED:
            logger.warning(f"⚠️ Circuit breaker '{self.name}': Failure {self.failure_count}/{self.failure_threshold}")

            if self.failure_count >= self.failure_threshold:
                # Too many failures, open circuit
                self.state = CircuitState.OPEN
                logger.error(f"🚨 Circuit breaker '{self.name}': CLOSED → OPEN (service down)")

    def reset(self):
        """Manually reset circuit breaker (for testing/admin)"""
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        logger.info(f"🔄 Circuit breaker '{self.name}': Manually reset to CLOSED")

    def get_state(self) -> dict:
        """Get current circuit breaker state"""
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "last_failure_time": self.last_failure_time.isoformat() if self.last_failure_time else None,
            "time_until_recovery": self._time_until_recovery()
        }

    def _time_until_recovery(self) -> Optional[int]:
        """Seconds until circuit will try recovery (half-open)"""
        if self.state == CircuitState.OPEN and self.last_failure_time:
            elapsed = (datetime.now() - self.last_failure_time).total_seconds()
            remaining = max(0, self.recovery_timeout - elapsed)
            return int(remaining)
        return None


# Global circuit breakers for external services
_circuit_breakers = {}


def get_circuit_breaker(
    name: str,
    failure_threshold: int = 5,
    recovery_timeout: int = 60,
    expected_exception: type = Exception
) -> CircuitBreaker:
    """
    Get or create circuit breaker for a service

    Args:
        name: Service name (e.g., 'gemini_api', 'sendgrid', 'stripe')
        failure_threshold: Failures before opening
        recovery_timeout: Seconds before retry
        expected_exception: Exception type to catch

    Returns:
        CircuitBreaker instance
    """
    if name not in _circuit_breakers:
        _circuit_breakers[name] = CircuitBreaker(
            name=name,
            failure_threshold=failure_threshold,
            recovery_timeout=recovery_timeout,
            expected_exception=expected_exception
        )
    return _circuit_breakers[name]


def circuit_breaker(
    name: str,
    failure_threshold: int = 5,
    recovery_timeout: int = 60,
    expected_exception: type = Exception,
    fallback: Optional[Callable] = None
):
    """
    Decorator for circuit breaker pattern

    Usage:
        @circuit_breaker(
            name="gemini_api",
            failure_threshold=5,
            recovery_timeout=60,
            expected_exception=httpx.HTTPError,
            fallback=lambda *args, **kwargs: {"cached": True}
        )
        async def call_gemini_api(prompt: str):
            return await gemini_client.generate(prompt)

    Args:
        name: Service name
        failure_threshold: Failures before opening circuit
        recovery_timeout: Seconds before retry
        expected_exception: Exception type to catch
        fallback: Optional fallback function if circuit open
    """
    def decorator(func: Callable):
        cb = get_circuit_breaker(name, failure_threshold, recovery_timeout, expected_exception)

        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await cb.call(func, *args, **kwargs)
            except CircuitBreakerOpenError:
                if fallback:
                    logger.info(f"Circuit breaker '{name}' open, using fallback")
                    return await fallback(*args, **kwargs) if asyncio.iscoroutinefunction(fallback) else fallback(*args, **kwargs)
                raise

        return wrapper
    return decorator


# Pre-configured circuit breakers for common services
gemini_circuit_breaker = get_circuit_breaker(
    name="gemini_api",
    failure_threshold=5,
    recovery_timeout=60,
    expected_exception=Exception  # Update with actual Gemini exception type
)

sendgrid_circuit_breaker = get_circuit_breaker(
    name="sendgrid",
    failure_threshold=3,
    recovery_timeout=30,
    expected_exception=Exception  # Update with SendGrid exception
)

stripe_circuit_breaker = get_circuit_breaker(
    name="stripe",
    failure_threshold=3,
    recovery_timeout=45,
    expected_exception=Exception  # Update with Stripe exception
)


def get_all_circuit_breakers_status() -> dict:
    """Get status of all circuit breakers"""
    return {name: cb.get_state() for name, cb in _circuit_breakers.items()}
