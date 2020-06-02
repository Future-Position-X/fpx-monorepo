FROM tiangolo/uwsgi-nginx-flask:python3.8
#RUN apk --update add bash nano && \
#apk add --no-cache postgresql-libs geos lapack openblas libstdc++ && \
#apk add --no-cache --virtual .build-deps postgresql-dev g++ gcc gfortran musl-dev cython lapack-dev openblas-dev
ENV STATIC_URL /static
ENV STATIC_PATH /var/www/app/static
COPY ./requirements.txt /var/www/requirements.txt
RUN pip install -r /var/www/requirements.txt
EXPOSE 80
ENV JWT_SECRET postgresql://master:lN1Pb60MO6sC@gia-dev.cjesin4yac8j.eu-north-1.rds.amazonaws.com:5432/gia
ENV DATABASE_URL mRJZQrLE6HlStXd4eEQcMLNDDIltgo1eYUzA5TbAcaRlwCX6FI2SLYKjgq19
COPY . /app

