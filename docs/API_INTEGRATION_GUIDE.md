# API Integration Guide

## Overview

This guide provides detailed information about integrating with external APIs used in the Children's Book Generator project.

## 1. Canva Connect API

### Authentication

Canva uses OAuth 2.0 for authentication. Here's how to set it up:

```python
from canva import CanvaClient

# Initialize the client
client = CanvaClient(
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET",
    redirect_uri="YOUR_REDIRECT_URI"
)

# Get authorization URL
auth_url = client.get_authorization_url(
    scopes=[
        "design:content:read",
        "design:content:write",
        "asset:read",
        "asset:write",
        "brandtemplate:read",
        "brandtemplate:meta:read"
    ]
)

# Exchange code for access token
tokens = client.exchange_code_for_token(authorization_code)
```

### Key Endpoints

#### Create Design
```python
async def create_design(self, template_id: str, title: str):
    design = await client.create_design(
        template_id=template_id,
        title=title,
        asset_id="optional_asset_id"
    )
    return design
```

#### Autofill Design
```python
async def autofill_design(self, brand_template_id: str, data: dict):
    job = await client.create_design_autofill_job(
        brand_template_id=brand_template_id,
        data=data
    )
    
    # Poll for completion
    while job.status == "in_progress":
        await asyncio.sleep(2)
        job = await client.get_design_autofill_job(job.id)
    
    return job.result
```

#### Export Design
```python
async def export_design(self, design_id: str, format: str = "pdf"):
    export_job = await client.create_design_export_job(
        design_id=design_id,
        format=format,
        quality="print",
        pages="all"
    )
    
    # Poll for completion
    while export_job.status == "in_progress":
        await asyncio.sleep(2)
        export_job = await client.get_design_export_job(export_job.id)
    
    return export_job.urls
```

### Rate Limits

- 60 requests per minute for most endpoints
- 10 concurrent export jobs
- 5 concurrent autofill jobs

### Error Handling

```python
from canva.exceptions import CanvaAPIError, RateLimitError

try:
    design = await client.create_design(...)
except RateLimitError:
    # Wait and retry
    await asyncio.sleep(60)
    design = await client.create_design(...)
except CanvaAPIError as e:
    logger.error(f"Canva API error: {e}")
    # Handle specific error
```

## 2. OpenAI API

### Authentication

```python
import openai

openai.api_key = "YOUR_API_KEY"
```

### GPT-4 Integration

#### Story Generation
```python
async def generate_story(self, prompt: str, age_group: str):
    response = await openai.ChatCompletion.acreate(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": f"You are a children's book author writing for {age_group} year olds."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.7,
        max_tokens=2000
    )
    
    return response.choices[0].message.content
```

### DALL-E 3 Integration

#### Image Generation
```python
async def generate_image(self, prompt: str, style: str = "vivid"):
    response = await openai.Image.acreate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        quality="hd",
        style=style,
        n=1
    )
    
    return response.data[0].url
```

#### Advanced Image Generation
```python
async def generate_character_image(self, character_description: str):
    # Add specific instructions for consistency
    enhanced_prompt = f"""
    Children's book illustration of {character_description}.
    Style: Whimsical, colorful, friendly for young children.
    Consistent character design with clear features.
    High contrast and vibrant colors.
    Simple background.
    """
    
    return await self.generate_image(enhanced_prompt)
```

### Rate Limits

- GPT-4: 10,000 tokens per minute
- DALL-E 3: 5 requests per minute
- Different limits for different tiers

### Error Handling

```python
import openai
from openai.error import RateLimitError, APIError

async def generate_with_retry(self, func, *args, **kwargs):
    max_retries = 3
    retry_delay = 1
    
    for attempt in range(max_retries):
        try:
            return await func(*args, **kwargs)
        except RateLimitError:
            if attempt < max_retries - 1:
                await asyncio.sleep(retry_delay * (2 ** attempt))
            else:
                raise
        except APIError as e:
            logger.error(f"OpenAI API error: {e}")
            raise
```

## 3. Best Practices

### API Key Management

```python
import os
from dotenv import load_dotenv

load_dotenv()

class APIConfig:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    CANVA_CLIENT_ID = os.getenv("CANVA_CLIENT_ID")
    CANVA_CLIENT_SECRET = os.getenv("CANVA_CLIENT_SECRET")
    
    @classmethod
    def validate(cls):
        required = [
            "OPENAI_API_KEY",
            "CANVA_CLIENT_ID",
            "CANVA_CLIENT_SECRET"
        ]
        
        missing = [key for key in required if not getattr(cls, key)]
        if missing:
            raise ValueError(f"Missing required API keys: {missing}")
```

### Caching Strategy

```python
import redis
from functools import wraps

redis_client = redis.Redis.from_url(os.getenv("REDIS_URL"))

def cache_result(expire_time=3600):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Create cache key
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Try to get from cache
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            
            # Generate result
            result = await func(*args, **kwargs)
            
            # Cache result
            redis_client.setex(
                cache_key,
                expire_time,
                json.dumps(result)
            )
            
            return result
        return wrapper
    return decorator
```

### Monitoring and Logging

```python
import logging
from prometheus_client import Counter, Histogram

# Metrics
api_requests = Counter(
    'api_requests_total',
    'Total API requests',
    ['service', 'endpoint', 'status']
)

api_latency = Histogram(
    'api_request_duration_seconds',
    'API request latency',
    ['service', 'endpoint']
)

# Logging
logger = logging.getLogger(__name__)

async def monitored_api_call(service: str, endpoint: str, func, *args, **kwargs):
    start_time = time.time()
    
    try:
        result = await func(*args, **kwargs)
        api_requests.labels(service, endpoint, 'success').inc()
        return result
    except Exception as e:
        api_requests.labels(service, endpoint, 'error').inc()
        logger.error(f"{service} API error on {endpoint}: {e}")
        raise
    finally:
        duration = time.time() - start_time
        api_latency.labels(service, endpoint).observe(duration)
```

## 4. Integration Patterns

### Async Queue Pattern

```python
from asyncio import Queue
import asyncio

class APIQueue:
    def __init__(self, rate_limit: int = 60):
        self.queue = Queue()
        self.rate_limit = rate_limit
        self.processing = False
    
    async def add_request(self, func, *args, **kwargs):
        await self.queue.put((func, args, kwargs))
        if not self.processing:
            asyncio.create_task(self._process_queue())
    
    async def _process_queue(self):
        self.processing = True
        
        while not self.queue.empty():
            func, args, kwargs = await self.queue.get()
            
            try:
                result = await func(*args, **kwargs)
                # Handle result
            except Exception as e:
                logger.error(f"Queue processing error: {e}")
            
            # Rate limiting
            await asyncio.sleep(60 / self.rate_limit)
        
        self.processing = False
```

### Fallback Pattern

```python
class APIFallbackHandler:
    def __init__(self):
        self.providers = {
            'primary': self.primary_api_call,
            'secondary': self.secondary_api_call,
            'fallback': self.fallback_api_call
        }
    
    async def make_request(self, *args, **kwargs):
        for provider_name, provider_func in self.providers.items():
            try:
                return await provider_func(*args, **kwargs)
            except Exception as e:
                logger.warning(f"{provider_name} failed: {e}")
                if provider_name == 'fallback':
                    raise
        
        raise Exception("All API providers failed")
```

## 5. Testing

### Mock API Responses

```python
from unittest.mock import Mock, patch
import pytest

@pytest.fixture
def mock_openai():
    with patch('openai.ChatCompletion.acreate') as mock:
        mock.return_value = Mock(
            choices=[Mock(message=Mock(content="Test story"))]
        )
        yield mock

@pytest.fixture
def mock_canva():
    with patch('canva.CanvaClient') as mock:
        client = Mock()
        client.create_design.return_value = Mock(id="design_123")
        mock.return_value = client
        yield mock

async def test_story_generation(mock_openai):
    service = ContentGenerationService()
    story = await service.generate_story("Test prompt", "5-7")
    
    assert story == "Test story"
    mock_openai.assert_called_once()
```

### Integration Tests

```python
@pytest.mark.integration
async def test_full_book_generation():
    # This test uses real APIs with test accounts
    service = BookGenerationService()
    
    book = await service.generate_book(
        title="Test Book",
        age_group="5-7",
        theme="adventure"
    )
    
    assert book.pdf_url is not None
    assert len(book.pages) >= 24
```

## 6. Common Issues and Solutions

### Issue: Rate Limiting
**Solution**: Implement exponential backoff and request queuing

### Issue: API Timeouts
**Solution**: Set appropriate timeouts and implement retry logic

### Issue: Inconsistent Image Generation
**Solution**: Use detailed prompts and style guidelines

### Issue: Large File Uploads
**Solution**: Use chunked uploads and progress tracking

### Issue: Token Limits
**Solution**: Implement text chunking and summarization

## 7. Security Considerations

1. Never expose API keys in client-side code
2. Use environment variables for sensitive data
3. Implement request signing where required
4. Validate all input data before API calls
5. Use HTTPS for all API communications
6. Implement proper error handling to avoid exposing sensitive information
7. Regularly rotate API keys
8. Monitor API usage for unusual patterns

## 8. Performance Optimization

1. Batch API requests where possible
2. Implement caching for frequently accessed data
3. Use webhook callbacks instead of polling where available
4. Optimize image sizes before upload
5. Use CDN for serving generated content
6. Implement connection pooling
7. Use async/await for concurrent operations
8. Monitor and optimize API response times
