First start db
`docker-compose up -d db`
Then we need to create and seed the db
`docker-compose run backend bash`
Within the container run
`alembic upgrade head`
Exit the container
`exit`
Then start the full stack
`docker-compose up -d`
