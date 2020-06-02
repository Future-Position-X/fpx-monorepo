#!/bin/bash
app="geo-api.dev"
docker run --rm -p 56733:80 \
  --env DATABASE_URL=postgresql://master:lN1Pb60MO6sC@gia-dev.cjesin4yac8j.eu-north-1.rds.amazonaws.com:5432/gia \
  --env JWT_SECRET=mRJZQrLE6HlStXd4eEQcMLNDDIltgo1eYUzA5TbAcaRlwCX6FI2SLYKjgq19 \
  --name=${app} \
  -v "/${PWD}:/app" ${app}