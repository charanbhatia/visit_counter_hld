# Website Visit Counter

A progressive implementation of a scalable website visit counter system, developed through five distinct tasks.

## Features by Implementation Stage

### Task 1: Basic Counter ✅
- FastAPI-based visit counter
- In-memory storage
- Basic POST/GET endpoints
- Simple response format

### Task 2: Redis Integration ✅
- Persistent Redis storage
- Docker Compose setup
- Data type handling
- Counter persistence

### Task 3: Application Cache ✅
- Local caching (5s TTL)
- Dual-layer read strategy
- Cache invalidation
- Performance optimization

### Task 4: Write Batching ✅
- Write buffer implementation
- 30-second flush interval
- Combined count calculation
- Optimized Redis operations

### Task 5: Redis Sharding ✅
- Dual Redis setup
- Consistent hashing
- Shard-specific responses
- Failover handling

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.9+
- Redis 6.2+

### Installation

1. Clone the repository:
```bash
git clone https://github.com/charanbhatia/visit_counter_hld
cd visit_counter_hld
```

2. Start with Docker Compose:
```bash
docker compose up --build
```

This starts:
- FastAPI application (port 8000)
- Redis shard 1 (port 7070)
- Redis shard 2 (port 7071)

### Local Development

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run application:
```bash
uvicorn main:app --reload
```

## API Usage

### Increment Visit Count
```bash
curl -X POST http://localhost:8000/visits/page1
```

Example response:
```json
{
    "visits": 10,
    "served_via": "redis_7070"
}
```

### Get Visit Count
```bash
curl http://localhost:8000/visits/page1
```

Example response:
```json
{
    "visits": 10,
    "served_via": "in_memory"
}
```

### Check Health
```bash
curl http://localhost:8000/health
```

## Response Formats

### Basic Counter (Task 1)
```json
{
    "visits": 10,
    "served_via": "in_memory"
}
```

### Redis Counter (Task 2)
```json
{
    "visits": 10,
    "served_via": "redis"
}
```

### Cached Counter (Task 3)
```json
{
    "visits": 10,
    "served_via": "in_memory"  // or "redis"
}
```

### Batched Counter (Task 4)
```json
{
    "visits": 10,
    "served_via": "batch"
}
```

### Sharded Counter (Task 5)
```json
{
    "visits": 10,
    "served_via": "redis_7070"  // or "redis_7071"
}
```

## Testing

### Unit Tests
```bash
pytest tests/unit/
```

### Integration Tests
```bash
pytest tests/integration/
```

### Performance Tests
```bash
pytest tests/performance/
```

## Documentation
- API Documentation: 
- Website Visit Counter Documentation: https://scythe-columnist-019.notion.site/Detailed-Website-Visit-Counter-System-1a2cfc8a0c6d8004839cc2c91c9847b8

## License
MIT License - see [LICENSE](LICENSE) file
