# Quick Start Guide

## Prerequisites

- Python 3.10 or higher
- PostgreSQL database
- Redis
- API keys for OpenAI and Canva

## Setup Instructions

### 1. Clone the Repository

```bash
cd /Users/englarmerdgemongwe/My-Projects/kids-book-generator
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` file and add your API keys:
- OpenAI API key
- Canva client ID and secret
- Database credentials

### 5. Set Up Database

```bash
# Create database
createdb kids_book_generator

# Run migrations (once we have them)
alembic upgrade head
```

### 6. Start Redis

```bash
redis-server
```

### 7. Run the Application

```bash
# Start the API server
uvicorn src.main:app --reload

# In another terminal, start the Celery worker
celery -A src.worker worker --loglevel=info
```

### 8. Access the Application

Open your browser and navigate to:
- Application: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## First Steps

1. **Create a Book Configuration**
   - Choose book type (story or coloring)
   - Select age group
   - Define theme and educational focus
   - Set page count

2. **Generate Content**
   - System will generate story using GPT-4
   - Create illustrations using DALL-E 3
   - Format according to Amazon KDP specs

3. **Review and Export**
   - Preview generated book
   - Make any necessary adjustments
   - Export as print-ready PDF

## API Usage

### Generate a Story Book

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/books/generate",
    json={
        "title": "The Magical Forest Adventure",
        "book_type": "story",
        "age_group": "5-7",
        "theme": "adventure",
        "page_count": 24
    }
)

book_id = response.json()["id"]
```

### Check Generation Status

```python
response = requests.get(f"http://localhost:8000/api/v1/books/{book_id}/status")
status = response.json()["status"]
```

### Download Generated Book

```python
response = requests.get(f"http://localhost:8000/api/v1/books/{book_id}/download")
with open("book.pdf", "wb") as f:
    f.write(response.content)
```

## Troubleshooting

### Common Issues

1. **API Key Errors**
   - Verify API keys in `.env` file
   - Check API quotas and limits

2. **Database Connection Issues**
   - Ensure PostgreSQL is running
   - Verify database credentials

3. **Redis Connection Issues**
   - Start Redis server
   - Check Redis URL in configuration

4. **Image Generation Failures**
   - Check DALL-E 3 API status
   - Verify prompt compliance with OpenAI policies

### Getting Help

- Check the [API Documentation](API_INTEGRATION_GUIDE.md)
- Review the [Technical Architecture](TECHNICAL_ARCHITECTURE.md)
- See the [TODO List](TODO.md) for current development status

## Next Steps

1. Explore the API documentation
2. Create your first book
3. Customize templates
4. Set up batch processing
5. Configure automated workflows
