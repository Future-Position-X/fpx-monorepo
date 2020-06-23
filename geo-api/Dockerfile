FROM tiangolo/uwsgi-nginx-flask:python3.8
#RUN apk --update add bash nano && \
#apk add --no-cache postgresql-libs geos lapack openblas libstdc++ && \
#apk add --no-cache --virtual .build-deps postgresql-dev g++ gcc gfortran musl-dev cython lapack-dev openblas-dev
ENV STATIC_URL /static
ENV STATIC_PATH /var/www/app/static
COPY ./requirements.txt /var/www/requirements.txt
RUN pip install -r /var/www/requirements.txt
EXPOSE 80
COPY . /app

