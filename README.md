# pers (under construction)

A project with [Typesense](https://typesense.org/) (No PhD required) in the backend, 
[Starlette](https://www.starlette.io/) with [Jinja2 templates](https://jinja.palletsprojects.com/en/stable/) as the 
frontend, and [Docker](https://www.docker.com/) for containerization, to be deployed to 
[Hetzner](https://www.hetzner.com/).

A project started at the 
[RIPE NCC Green Tech Hackathon](https://labs.ripe.net/author/becha/celebrating-green-tech-hackathon-results/), and 
the first index is made from OSSFinder scraped data, also see [oss4climate](https://github.com/Pierre-VF/oss4climate).

## Development

### Services

Start all services:

```commandline
docker-compose -f docker-compose.dev.yml up --build
```

Stop the current containers: 

```commandline
docker-compose -f docker-compose.dev.yml down
```

Rebuild: 

```commandline
docker-compose -f docker-compose.dev.yml build
```

Start: 

```commandline
docker-compose -f docker-compose.dev.yml up
```

Run tests:

```commandline
docker-compose -f docker-compose.dev.yml --profile test up backend-tests frontend-tests
```

### Accessing services

* Frontend: http://localhost:8001
* Backend: http://localhost:8000
* Nginx: http://localhost:8080

### Verifying

Verify Typesense is working from within the backend container:

```commandline
docker exec -it backend-app-dev curl http://typesense:8108/health
```

(Should return `{"ok":true})`

Checks from the host machine:

```commandline
curl http://localhost:8108/health
```

Should also return `{"ok":true}` if ports are mapped correctly)

Check backend health:

```commandline
curl http://localhost:8000/health
```

Should return `{"status":"healthy"}`

Check frontend:

```commandline
curl -I http://localhost:8001
```

Should return `200 OK`

### Run the tests

```commandline
docker-compose -f docker-compose.dev.yml --profile test up backend-tests frontend-tests
```

### Roadmap

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

## Production

### Generate hashes for requirements

```commandline
pip install hashin
```

For backend:

```commandline
cd backend
hashin -r requirements.txt $(cat requirements.txt | cut -d'=' -f1 | cut -d'>' -f1 | cut -d'<' -f1)
```

For frontend:

```commandline
cd frontend
hashin -r requirements.txt $(cat requirements.txt | cut -d'=' -f1 | cut -d'>' -f1 | cut -d'<' -f1)
```

To deploy:

```commandline
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```
