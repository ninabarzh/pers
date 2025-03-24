# pers (under construction)

A project with [Typesense](https://typesense.org/) (No PhD required) in the backend, 
[Starlette](https://www.starlette.io/) with [Jinja2 templates](https://jinja.palletsprojects.com/en/stable/) as the 
frontend, and [Docker](https://www.docker.com/) for containerization, to be deployed to 
[Hetzner](https://www.hetzner.com/).

A project started at the 
[RIPE NCC Green Tech Hackathon](https://labs.ripe.net/author/becha/celebrating-green-tech-hackathon-results/), and 
the first index is made from OSSFinder scraped data, also see [oss4climate](https://github.com/Pierre-VF/oss4climate).

## Development

### Build and run the containers

```commandline
docker-compose --env-file .env.dev up
```

Down (and remove):
```commandline
docker-compose down
```

### Run the tests

To run services with the test profile:

```commandline
docker-compose --profile test up
```

```commandline
docker-compose run backend-tests
```

```commandline
docker-compose run frontend-tests
```

### Roadmap

- [x] Typesense, backend and frontend dockers.
- [x] Upload and search routes.
- [x] Set up test framework and first tests.
- [x] Add pagination to handle large result sets. Typesense supports pagination via the page and per_page parameters.
- [x] Improve error handling in the frontend to display user-friendly error messages.
- [x] Add CSS to make the frontend more visually appealing.
- [x] Refactoring (1)
- [x] Improve the dockers' robustness.
- [ ] Relevancy ranking.
- [ ] Add filters to narrow down search results (e.g., filter by organisation or license).
- [ ] Use Typesense's highlighting feature to highlight search terms in the results.
- [ ] Add user authentication to restrict access to the upload page.
- [ ] Refactoring (2)
- [ ] Deploy the application to Hetzner.
- [ ] Consider scaling Typesense horizontally by adding more nodes to the cluster.
- [ ] Set up regular backups of the Typesense data directory to ensure data safety.
- [ ] Add monitoring and alerting for Typesense to track performance and detect issues early.
- [ ] Facets.
- [ ] Create a new index page with user authentication.
- [ ] When uploading a `.json` file as index, be able to choose which index to upload to.

## Production

Start the production services:

```commandline
docker-compose --env-file .env.prod up -d
```

Stop the production services:

```commandline
docker-compose -f docker-compose.prod.yml down
```
    
View Logs:

```commandline
docker-compose -f docker-compose.yml logs -f
```
