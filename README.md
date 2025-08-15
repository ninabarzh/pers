# Pers - Open Sustainability Search 

[![Docker Containers](https://img.shields.io/badge/Docker%20Containers-4%20services-blue?logo=docker)](https://github.com/ninabarzh/pers/blob/main/docker-compose.prod.yml) [![Deployment Status](https://img.shields.io/github/actions/workflow/status/ninabarzh/pers/deploy.yml?label=Hetzner%20Deploy&logo=hetzner)](https://github.com/ninabarzh/pers/actions/workflows/deploy.yml) [![Tea Approved](https://img.shields.io/badge/Tea%20Approved-3%20cups%20a%20day-yellowgreen)](https://github.com/ninabarzh/pers)

**Self-hosted search for greener technology, communities and houses**  

*Deployed at [finder.green](https://finder.green) | [Roadmap](https://github.com/ninabarzh/pers/wiki)*  

## Core Technology  

### Search Engine  
- **Typesense** for lightning-fast, typo-tolerant search  
- Custom ranking for sustainability metrics  
- Real-time index updates  

### Stack  
| Component       | Technology          | Purpose                          |  
|-----------------|---------------------|----------------------------------|  
| **Backend**     | Python/Starlette    | Search API, data processing      |  
| **Frontend**    | Jinja2 + Bootstrap  | Responsive interface             |  
| **Infra**       | Docker + Nginx      | Scalable deployment              |  

## Quick Start  

### Development  
```bash  
git clone https://github.com/ninabarzh/pers.git  
cd pers  
docker-compose -f docker-compose.yml up -d  
```

This starts:  

- Search API (8000)  
- Typesense (8108)  
- Web UI (8001) 
- Nginx (8080)

#### Testing with Docker

Running all tests

```commandline
# Backend tests
docker-compose run --rm backend-tests

# Frontend tests 
docker-compose run --rm frontend-tests
```

Running specific tests:

```commandline
# Run single test file
docker-compose run --rm backend-tests pytest tests/test_routes.py

# Run specific test
docker-compose run --rm backend-tests pytest tests/test_routes.py::test_search_endpoint -v

# Run with debug output
docker-compose run --rm backend-tests pytest -xvs
```

### Production Deployment

To use with GitHub Actions: `./deploy.sh`

```commandline
- name: Deploy
  env:
    PROD_DOMAIN: ${{ secrets.PROD_DOMAIN }}
    TYPESENSE_API_KEY: ${{ secrets.TYPESENSE_API_KEY }}
    PROTON_SMTP_CREDENTIALS: ${{ secrets.PROTON_SMTP_CREDENTIALS }}
    FRIENDLY_CAPTCHA_SECRET: ${{ secrets.FRIENDLY_CAPTCHA_SECRET }}
    CSRF_SECRET_KEY: ${{ secrets.CSRF_SECRET_KEY }}
  run: |
    ssh deploy@${{ secrets.SERVER_IP }} "cd /home/deploy/app && ./deploy.sh"
```
But also see the somewhat more complex [deploy.yml](https://github.com/ninabarzh/pers/blob/main/.github/workflows/deploy.yml)

#### Deployment requirements  

- Ubuntu 22.04  
- 4GB RAM  
- Domain (DNS configured)  

### Search Features

#### Query Syntax

| Example	         | Description                         |
|------------------|-------------------------------------|
| renewable energy | Basic term matching                 |
| \[energy]	       | Field-specific search               |
| linux ~2	        | Fuzzy match (2-character tolerance) |

#### Indexing Pipeline

Data Ingestion

* OSSFinder climate projects (more to follow)
* Custom CSV/JSON imports

Normalization

* Deduplication
* Sustainability scoring

Real-time Updates

```python
# Example Typesense update  
client.collections['projects'].documents.upsert({  
  'id': 'proj_123',  
  'name': 'SolarMesh',  
  'impact_score': 8.2  
}) 
```

### Architecture

```commandline
pers/  
├── backend/  
│   ├── src/app/  
│   │   ├── routes/search.py    # Query handling  
│   │   └── typesense_client.py # Index management  
├── frontend/  
│   └── templates/search.html   # Results rendering  
└── data/  
    └── typesense/              # Persistent search indices  
```

### Maintenance

#### Backup/Restore

```bash
# Backup  
docker exec typesense-db \  
  tar czvf /data/backup.tar.gz /data/typesense  

# Restore  
docker exec -it typesense-db \  
  tar xzvf /data/backup.tar.gz -C / 
```

#### Monitoring

```bash
# Check search latency  
curl "http://localhost:8108/health"  

# Log inspection  
docker-compose logs -f typesense  
```

### Why Self-Hosted?

* Privacy: No user tracking
* Customization: Tailor rankings to your sustainability criteria
* Offline Capable: Air-gapped deployment supported

### License 

This is free and unencumbered software released into the public domain (Unlicense).


