## How to start

Either run this container directly with *docker-compose* or build and run with *docker*.

#docker-compose
```
docker-compose -f docker-compose.prod.yml up --build
```

#docker
```
docker build --tag songlen:1.0 .
docker run --detach --env PORT=5000 --publish 5000:5000 --name songlen songlen:1.0
```

#frontend
After the container started the frontend can be accessed on http://localhost:5000.
