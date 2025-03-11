"""
Resilience patterns for the Universal Connector Block implementation.
"""

import time
import hashlib
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("ucb.resilience")


class CircuitBreaker:
    """Implements circuit breaker pattern for resilient API calls."""
    
    def __init__(self, failure_threshold: int = 5, reset_timeout: int = 60):
        """
        Initialize a new circuit breaker.
        
        Args:
            failure_threshold: Number of failures before the circuit opens
            reset_timeout: Seconds to wait before trying to reset the circuit
        """
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        logger.debug(f"CircuitBreaker initialized with threshold={failure_threshold}, timeout={reset_timeout}")
        
    def record_success(self):
        """Record a successful call."""
        if self.state == "HALF_OPEN":
            logger.info("Circuit reset to CLOSED after successful call in HALF_OPEN state")
        self.failure_count = 0
        self.state = "CLOSED"
        
    def record_failure(self):
        """Record a failed call."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold and self.state != "OPEN":
            logger.warning(f"Circuit OPEN after {self.failure_count} failures")
            self.state = "OPEN"
            
    def allow_request(self) -> bool:
        """Check if a request should be allowed."""
        if self.state == "CLOSED":
            return True
            
        if self.state == "OPEN":
            # Check if reset timeout has elapsed
            if self.last_failure_time:
                elapsed = time.time() - self.last_failure_time
                if elapsed > self.reset_timeout:
                    logger.info(f"Circuit switching to HALF_OPEN after {elapsed:.2f}s")
                    self.state = "HALF_OPEN"
                    return True
            return False
            
        if self.state == "HALF_OPEN":
            return True
            
        return True
    
    @property
    def is_open(self) -> bool:
        """Check if the circuit is open."""
        return self.state == "OPEN"
        
    def reset(self):
        """Manually reset the circuit breaker."""
        logger.info("Circuit manually reset to CLOSED")
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"


class RateLimiter:
    """Implements rate limiting for API calls."""
    
    def __init__(self, calls_per_minute: int = 60):
        """
        Initialize a new rate limiter.
        
        Args:
            calls_per_minute: Maximum number of calls allowed per minute
        """
        self.calls_per_minute = calls_per_minute
        self.call_history = []
        logger.debug(f"RateLimiter initialized with {calls_per_minute} calls per minute")
        
    def allow_request(self) -> bool:
        """Check if a request should be allowed based on rate limits."""
        now = time.time()
        
        # Remove calls older than 1 minute
        self.call_history = [timestamp for timestamp in self.call_history 
                             if (now - timestamp) < 60]
                             
        # Check if we're under the limit
        if len(self.call_history) < self.calls_per_minute:
            self.call_history.append(now)
            return True
            
        logger.warning(f"Rate limit of {self.calls_per_minute} calls per minute exceeded")
        return False
    
    @property
    def remaining(self) -> int:
        """Get the number of remaining calls in the current window."""
        self.allow_request()  # This will clean up expired calls
        return max(0, self.calls_per_minute - len(self.call_history))
    
    @property
    def reset_time(self) -> float:
        """Get the time (in seconds) until the rate limit resets."""
        if not self.call_history:
            return 0
            
        oldest_call = min(self.call_history)
        return max(0, oldest_call + 60 - time.time())


class Cacher:
    """Implements caching for API responses."""
    
    def __init__(self, ttl_seconds: int = 300):
        """
        Initialize a new cacher.
        
        Args:
            ttl_seconds: Time-to-live for cache entries in seconds
        """
        self.cache = {}
        self.ttl_seconds = ttl_seconds
        logger.debug(f"Cacher initialized with TTL={ttl_seconds}s")
        
    def get(self, key: str) -> Optional[Any]:
        """Get a value from cache if available and not expired."""
        if key not in self.cache:
            return None
            
        entry = self.cache[key]
        if (time.time() - entry["timestamp"]) > self.ttl_seconds:
            # Entry expired
            logger.debug(f"Cache entry for {key} expired")
            del self.cache[key]
            return None
            
        logger.debug(f"Cache hit for {key}")
        return entry["value"]
        
    def set(self, key: str, value: Any):
        """Store a value in cache."""
        logger.debug(f"Caching value for {key}")
        self.cache[key] = {
            "value": value,
            "timestamp": time.time()
        }
        
    def generate_key(self, *args, **kwargs) -> str:
        """Generate a cache key from arguments."""
        key_parts = [str(arg) for arg in args]
        key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
        key_str = "::".join(key_parts)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def clear(self):
        """Clear all cache entries."""
        logger.debug("Clearing cache")
        self.cache = {}
    
    def clear_key(self, key: str):
        """Clear a specific cache entry."""
        if key in self.cache:
            logger.debug(f"Clearing cache entry for {key}")
            del self.cache[key]
    
    @property
    def size(self) -> int:
        """Get the number of entries in the cache."""
        return len(self.cache)
    
    @property
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        now = time.time()
        active_entries = 0
        expired_entries = 0
        
        for key, entry in self.cache.items():
            if (now - entry["timestamp"]) <= self.ttl_seconds:
                active_entries += 1
            else:
                expired_entries += 1
                
        return {
            "total_entries": len(self.cache),
            "active_entries": active_entries,
            "expired_entries": expired_entries,
            "ttl_seconds": self.ttl_seconds
        }


class Retrier:
    """Implements retry logic with backoff."""
    
    def __init__(self, max_attempts: int = 3, base_delay: float = 0.5, 
                 backoff_factor: float = 2.0, max_delay: float = 30.0):
        """
        Initialize a new retrier.
        
        Args:
            max_attempts: Maximum number of retry attempts
            base_delay: Initial delay in seconds
            backoff_factor: Multiplier for subsequent delays
            max_delay: Maximum delay in seconds
        """
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.backoff_factor = backoff_factor
        self.max_delay = max_delay
        logger.debug(f"Retrier initialized with max_attempts={max_attempts}, "
                    f"base_delay={base_delay}, backoff_factor={backoff_factor}")
        
    def get_delay(self, attempt: int) -> float:
        """Calculate the delay for a given attempt."""
        delay = self.base_delay * (self.backoff_factor ** (attempt - 1))
        return min(delay, self.max_delay)
    
    async def execute_async(self, func, *args, **kwargs):
        """Execute an async function with retries."""
        import asyncio
        
        attempt = 0
        last_error = None
        
        while attempt < self.max_attempts:
            try:
                attempt += 1
                return await func(*args, **kwargs)
            except Exception as e:
                last_error = e
                if attempt < self.max_attempts:
                    delay = self.get_delay(attempt)
                    logger.warning(f"Attempt {attempt} failed: {str(e)}. "
                                  f"Retrying in {delay:.2f}s...")
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"All {self.max_attempts} attempts failed")
                    
        # If we got here, all attempts failed
        raise last_error
    
    def execute(self, func, *args, **kwargs):
        """Execute a function with retries."""
        attempt = 0
        last_error = None
        
        while attempt < self.max_attempts:
            try:
                attempt += 1
                return func(*args, **kwargs)
            except Exception as e:
                last_error = e
                if attempt < self.max_attempts:
                    delay = self.get_delay(attempt)
                    logger.warning(f"Attempt {attempt} failed: {str(e)}. "
                                  f"Retrying in {delay:.2f}s...")
                    time.sleep(delay)
                else:
                    logger.error(f"All {self.max_attempts} attempts failed")
                    
        # If we got here, all attempts failed
        raise last_error
