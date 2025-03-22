# pers (under construction)

A project with [Typesense](https://typesense.org/) (No PhD required) in the backend, 
[Starlette](https://www.starlette.io/) with [Jinja2 templates](https://jinja.palletsprojects.com/en/stable/) as the 
frontend, and [Docker](https://www.docker.com/) for containerization, to be deployed to 
[Hetzner](https://www.hetzner.com/) using [Sliplane](https://sliplane.io/).

A project started at the 
[RIPE NCC Green Tech Hackathon](https://labs.ripe.net/author/becha/celebrating-green-tech-hackathon-results/). 

The first index is made from OSSFinder scraped data, also see [oss4climate](https://github.com/Pierre-VF/oss4climate).

## Build and run the containers

Up (detached `-d`):
```commandline
docker-compose up -d --build
```

Down (and remove):
```commandline
docker-compose down
```

## Run the tests

```commandline
docker-compose run backend-tests
```

```commandline
docker-compose run frontend-tests
```
