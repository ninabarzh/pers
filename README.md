# Pers - Green Finder or Greener Find Search Engine

Pers is a self-hosted search engine combining [Typesense](https://typesense.org/) (No PhD required) in the backend, 
[Starlette](https://www.starlette.io/) with [Jinja2 templates](https://jinja.palletsprojects.com/en/stable/) in the 
frontend, and [Docker](https://www.docker.com/) for containerization, deployed to 
[Hetzner](https://www.hetzner.com/).

A project started at the 
[RIPE NCC Green Tech Hackathon](https://labs.ripe.net/author/becha/celebrating-green-tech-hackathon-results/), and 
the first index is made from OSSFinder scraped data, also see [oss4climate](https://github.com/Pierre-VF/oss4climate).

## Current features

- Full-text search with typo tolerance
- File upload & indexing (JSON)
- Fast API backend with Starlette
- Secure HTTPS with automatic Let's Encrypt

## Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- Python 3.10+ (for development)
- Node.js 16+ (for frontend development)

## Development

### Setup

Clone the repository:

```
git clone https://github.com/ninabarzh/pers.git
cd pers
```

Set up environment:

```
cp .env.example .env
```

Edit `.env` with your local values

Start services:

```
docker-compose -f docker-compose.yml up -d
```

Access services:

* Frontend: http://localhost:8001
* Backend API: http://localhost:8000
* Typesense: http://localhost:8108

### Development commands

Run backend tests:

```
cd backend && ./run_tests.sh
```

Run frontend tests:

```
cd frontend && ./run_tests.sh
```

Rebuild containers:

```
docker-compose -f docker-compose.yml build --no-cache
```

View logs:

```
docker-compose logs -f
```

## Production deployment

### Server preparation

- Ubuntu 22.04 LTS
- 2+ CPU cores
- 4GB+ RAM
- Domain name pointing to server

### Deployment steps

On your local machine:

```
git clone https://github.com/yourusername/pers.git
cd pers
```

Set up deployment secrets:

```
echo "PROD_DOMAIN=yourdomain.com" >> .env.prod
echo "PROD_TYPESENSE_API_KEY=$(openssl rand -hex 32)" >> .env.prod
```

Deploy to production:

```
./deploy.sh
```

3. Certificate Setup (First Time)

```
ssh deploy@your-server
cd ~/app
chmod +x init-letsencrypt.sh
./init-letsencrypt.sh
```

### Production URLs

- Web Interface: https://yourdomain.com
- API: https://yourdomain.com/api
- Admin: https://yourdomain.com/admin

### File Structure

```
pers/
├── backend/          # Python search backend
├── frontend/         # Web interface
├── nginx/            # Production web server config
├── data/             # Persistent data
├── docker-compose.yml       # Development setup
├── docker-compose.prod.yml  # Production setup
└── init-letsencrypt.sh      # SSL certificate setup
```

### Maintenance

Create backup of Typesense data:

```
docker exec -it typesense-db tar czvf /data/typesense-backup.tar.gz /data/typesense
```

### Monitoring

View running containers:

```
docker compose -f docker-compose.prod.yml ps
```

Check logs:

```
docker compose -f docker-compose.prod.yml logs -f
```

### Troubleshooting

- Issue: Typesense fails to start
- Fix: Check memory allocation - Typesense needs at least 2GB free memory

- Issue: Certificate generation fails
- Fix: Verify port 80 is open and domain DNS is properly configured

- Issue: File uploads failing
- Fix: Check client_max_body_size in nginx config

### License

This is free and unencumbered software released into the public domain.

## Roadmap

#### Getting started
- [x] Typesense, backend and frontend dockers.
- [x] Upload and search routes.
- [x] Set up test framework and first tests.
- [x] Add pagination to handle large result sets. Typesense supports pagination via the page and per_page parameters.
- [x] Improve error handling in the frontend to display user-friendly error messages.
- [x] Add CSS to make the frontend more visually appealing.
- [x] Refactoring (1)
- [x] Improve the dockers' robustness.

#### Testing
- [ ] A test helper function to handle HTML-encoded assertions
- [ ] Document the expected error message formats in API specs
- [ ] Set up test logging to capture full responses when debugging failures

#### Expanding search capabilities
- [ ] Relevancy ranking.
- [ ] Adding filters to narrow down search results (e.g., filter by organisation or license).
- [ ] Using Typesense's highlighting feature to highlight search terms in the results.
- [ ] Facets.

#### Engineering
- [ ] Initial production (the one to throw away).
- [ ] Refactoring (2)
- [ ] Deploy the application to Hetzner (2nd).
- [ ] Consider scaling Typesense horizontally by adding more nodes to the cluster.
- [ ] Set up regular backups of the Typesense data directory to ensure data safety.
- [ ] Add monitoring and alerting for Typesense to track performance and detect issues early.
- [ ] Implement a blue-green deployment strategy

#### Further development
- [ ] Add user authentication to restrict access to the upload page.
- [ ] Create a new index page with user authentication.
- [ ] When uploading a `.json` file as index, be able to choose which index to upload to.
