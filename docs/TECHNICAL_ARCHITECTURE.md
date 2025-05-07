# Technical Architecture Document

## System Overview

The Children's Book Generator is a microservices-based architecture that integrates multiple AI services and APIs to automatically generate children's books and coloring books for Amazon KDP.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Interface                            │
│                    (React Frontend)                              │
└─────────────────┬───────────────────────────┬──────────────────┘
                  │                           │
┌─────────────────▼──────────────┐ ┌─────────▼──────────────────┐
│        API Gateway             │ │      Admin Dashboard       │
│      (FastAPI + Auth)          │ │     (Management UI)        │
└─────────────────┬──────────────┘ └────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────────┐
│                     Application Services Layer                   │
├─────────────────┬──────────────┬──────────────┬───────────────┤
│ Content         │ Formatting   │ Canva        │ Storage       │
│ Generation      │ Service      │ Integration  │ Service       │
│ Service         │              │ Service      │               │
└─────────────────┴──────────────┴──────────────┴───────────────┘
                  │              │              │
┌─────────────────▼──────────────▼──────────────▼───────────────┐
│                    External Services Layer                      │
├─────────────────┬──────────────┬──────────────┬───────────────┤
│ OpenAI API      │ OpenAI API   │ Canva API    │ Cloud Storage │
│ (GPT-4)         │ (DALL-E 3)   │              │ (S3/GCS)      │
└─────────────────┴──────────────┴──────────────┴───────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────────┐
│                    Data Layer                                   │
├─────────────────┬──────────────┬───────────────────────────────┤
│ PostgreSQL      │ Redis        │ File System                   │
│ (Metadata)      │ (Cache)      │ (Temp Storage)                │
└─────────────────┴──────────────┴───────────────────────────────┘
```

## Component Details

### 1. Frontend Layer

#### React Application
- **Purpose**: User interface for book configuration and generation
- **Technologies**: React 18, TypeScript, Redux Toolkit
- **Features**:
  - Book configuration forms
  - Real-time preview
  - Progress tracking
  - Download management

### 2. API Gateway

#### FastAPI Backend
- **Purpose**: Central API gateway and authentication
- **Technologies**: FastAPI, Python 3.10+, JWT
- **Endpoints**:
  - `/api/v1/auth/*` - Authentication
  - `/api/v1/books/*` - Book management
  - `/api/v1/generate/*` - Generation tasks
  - `/api/v1/templates/*` - Template management

### 3. Application Services

#### Content Generation Service
```python
class ContentGenerationService:
    def __init__(self, openai_client, content_filter):
        self.openai_client = openai_client
        self.content_filter = content_filter
    
    async def generate_story(self, params: StoryParams) -> Story:
        # Story generation logic
        pass
    
    async def generate_image(self, prompt: str) -> Image:
        # Image generation logic
        pass
```

**Responsibilities**:
- Generate age-appropriate stories
- Create consistent character descriptions
- Generate illustration prompts
- Produce coloring book outlines

#### Formatting Service
```python
class FormattingService:
    def __init__(self, pdf_generator, kdp_validator):
        self.pdf_generator = pdf_generator
        self.kdp_validator = kdp_validator
    
    async def format_book(self, content: BookContent) -> FormattedBook:
        # Formatting logic
        pass
    
    async def generate_cover(self, book_meta: BookMetadata) -> Cover:
        # Cover generation logic
        pass
```

**Responsibilities**:
- Apply KDP formatting requirements
- Calculate bleeds and margins
- Generate covers with spine calculations
- Create print-ready PDFs

#### Canva Integration Service
```python
class CanvaIntegrationService:
    def __init__(self, canva_client, template_manager):
        self.canva_client = canva_client
        self.template_manager = template_manager
    
    async def create_design(self, template_id: str, data: dict) -> Design:
        # Design creation logic
        pass
    
    async def export_pdf(self, design_id: str) -> bytes:
        # PDF export logic
        pass
```

**Responsibilities**:
- Manage Canva templates
- Autofill designs with content
- Export high-quality PDFs
- Handle asset uploads

#### Storage Service
```python
class StorageService:
    def __init__(self, s3_client, db_client):
        self.s3_client = s3_client
        self.db_client = db_client
    
    async def store_book(self, book: GeneratedBook) -> str:
        # Storage logic
        pass
    
    async def retrieve_book(self, book_id: str) -> GeneratedBook:
        # Retrieval logic
        pass
```

**Responsibilities**:
- Store generated books
- Manage temporary files
- Handle asset storage
- Implement versioning

### 4. Data Models

#### Core Models
```python
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class BookMetadata(BaseModel):
    title: str
    author: str
    age_group: str
    book_type: str  # "story" or "coloring"
    theme: str
    educational_focus: Optional[str]
    trim_size: str
    page_count: int

class Story(BaseModel):
    chapters: List[Chapter]
    characters: List[Character]
    moral_lesson: Optional[str]
    
class Chapter(BaseModel):
    title: str
    content: str
    illustration_prompt: str
    
class Character(BaseModel):
    name: str
    description: str
    visual_description: str
    role: str

class GeneratedBook(BaseModel):
    id: str
    metadata: BookMetadata
    content: BookContent
    status: str
    created_at: datetime
    pdf_url: Optional[str]
```

### 5. Database Schema

#### PostgreSQL Tables
```sql
-- Books table
CREATE TABLE books (
    id UUID PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    author VARCHAR(255),
    book_type VARCHAR(50),
    status VARCHAR(50),
    metadata JSONB,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Generation tasks table
CREATE TABLE generation_tasks (
    id UUID PRIMARY KEY,
    book_id UUID REFERENCES books(id),
    task_type VARCHAR(50),
    status VARCHAR(50),
    parameters JSONB,
    result JSONB,
    created_at TIMESTAMP,
    completed_at TIMESTAMP
);

-- Templates table
CREATE TABLE templates (
    id UUID PRIMARY KEY,
    name VARCHAR(255),
    type VARCHAR(50),
    canva_template_id VARCHAR(255),
    parameters JSONB,
    created_at TIMESTAMP
);
```

### 6. Integration Patterns

#### API Integration Pattern
```python
class APIClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key
        self.session = httpx.AsyncClient()
    
    async def make_request(self, method: str, endpoint: str, **kwargs):
        # Implements retry logic, rate limiting, error handling
        pass
```

#### Queue-based Processing
```python
from celery import Celery

celery_app = Celery('book_generator')

@celery_app.task
def generate_book_task(book_id: str, params: dict):
    # Long-running book generation task
    pass
```

### 7. Security Architecture

#### Authentication & Authorization
- JWT-based authentication
- Role-based access control (RBAC)
- API key management for external services
- OAuth 2.0 for Canva integration

#### Data Security
- Encryption at rest for sensitive data
- TLS for all API communications
- Secure credential storage (AWS Secrets Manager)
- Content moderation and filtering

### 8. Deployment Architecture

#### Container Architecture
```yaml
version: '3.8'
services:
  api:
    image: book-generator-api:latest
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
    ports:
      - "8000:8000"
  
  worker:
    image: book-generator-worker:latest
    environment:
      - CELERY_BROKER_URL=${REDIS_URL}
    
  redis:
    image: redis:7-alpine
    
  postgres:
    image: postgres:15-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data
```

#### Kubernetes Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: book-generator-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: book-generator-api
  template:
    metadata:
      labels:
        app: book-generator-api
    spec:
      containers:
      - name: api
        image: book-generator-api:latest
        ports:
        - containerPort: 8000
```

### 9. Monitoring & Observability

#### Metrics
- Request latency
- API success/failure rates
- Generation task completion times
- Resource utilization

#### Logging
- Structured logging with correlation IDs
- Centralized log aggregation (ELK stack)
- Error tracking (Sentry)

#### Tracing
- Distributed tracing (OpenTelemetry)
- Request flow visualization
- Performance bottleneck identification

### 10. Scalability Considerations

#### Horizontal Scaling
- Stateless API services
- Distributed task queue
- Load balancing
- Auto-scaling based on metrics

#### Caching Strategy
- Redis for API response caching
- CDN for static assets
- Template caching
- Generated content caching

#### Performance Optimization
- Async/await for I/O operations
- Connection pooling
- Batch processing
- Image optimization

## Technology Stack Summary

### Backend
- Python 3.10+
- FastAPI
- Celery
- SQLAlchemy
- Pydantic

### Frontend
- React 18
- TypeScript
- Redux Toolkit
- Material-UI

### Infrastructure
- Docker
- Kubernetes
- PostgreSQL
- Redis
- MinIO/S3

### External Services
- OpenAI API
- Canva Connect API
- AWS/GCP services

### Monitoring
- Prometheus
- Grafana
- ELK Stack
- Sentry
