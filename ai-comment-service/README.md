# AI Comment Service

A microservice that generates sarcastic comments using Ollama and the TinyLlama model.

## Features

- Lightweight TinyLlama model (runs on weak devices)
- Generates short, sarcastic comments for posts
- REST API with Flask
- Health check endpoint
- Unit tests

## API Endpoints

### Health Check
```
GET /health
```

Response:
```json
{
  "status": "healthy",
  "model": "tinyllama"
}
```

### Generate Comment
```
POST /generate-comment
Content-Type: application/json

{
  "title": "Post title",
  "text": "Post content"
}
```

Response:
```json
{
  "comment": "Generated sarcastic comment",
  "generated_by": "AI (TinyLlama)"
}
```

## Running Tests

```bash
pytest test_app.py -v
```

## Model

Uses **TinyLlama** - a 1.1B parameter model that's optimized for low-resource environments while still providing decent text generation capabilities.
