# API Testing Commands

This file contains curl commands to manually test our API endpoints for the Phase 5 backend implementation.

## User Registration

```bash
curl -X POST http://localhost:8000/api/v1/users \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "Test1234!",
    "full_name": "Test User"
  }'
```

## User Authentication (Token Generation)

```bash
curl -X POST http://localhost:8000/api/v1/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=Test1234!"
```

## Book Creation (Save the token from the previous command)

```bash
export TOKEN="<paste_token_here>"

curl -X POST http://localhost:8000/api/v1/books \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "metadata": {
      "title": "Test Book",
      "book_type": "STORY",
      "trim_size": "SQUARE",
      "age_group": "EARLY_READER",
      "author": "Test Author",
      "theme": "Adventure",
      "page_count": 24
    },
    "template_id": "canva_story_square_dbfe88cd"
  }'
```

## Book Listing

```bash
curl -X GET http://localhost:8000/api/v1/books \
  -H "Authorization: Bearer $TOKEN"
```

## Batch Job Creation

```bash
curl -X POST http://localhost:8000/api/v1/batch \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "name": "Test Batch Job",
    "description": "A test batch job created via curl",
    "books": [
      {
        "metadata": {
          "title": "Batch Book 1",
          "description": "First book in batch",
          "book_type": "STORY", 
          "trim_size": "SQUARE",
          "age_group": "CHILDREN_5_8",
          "author": "Test Author",
          "language": "en",
          "keywords": ["test", "batch", "book1"],
          "pages": 24
        },
        "template_id": "canva_story_square_dbfe88cd"
      },
      {
        "metadata": {
          "title": "Batch Book 2",
          "description": "Second book in batch",
          "book_type": "COLORING",
          "trim_size": "STANDARD",
          "age_group": "CHILDREN_8_12",
          "author": "Test Author",
          "language": "en", 
          "keywords": ["test", "batch", "book2"],
          "pages": 32
        },
        "template_id": "canva_coloring_standard_f728f12b"
      }
    ]
  }'
```

## Test with Existing Users

You can also test with the pre-defined users in the fake database:

```bash
# Admin user
curl -X POST http://localhost:8000/api/v1/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin"

# Regular user
curl -X POST http://localhost:8000/api/v1/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user&password=user"
```

For debugging purposes, you might also want to inspect the JWT token contents:

```bash
# Decode JWT token (replace TOKEN with your actual token)
echo $TOKEN | cut -d'.' -f2 | base64 -d 2>/dev/null | python -m json.tool
```
