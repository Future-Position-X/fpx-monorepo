FROM fpxgia/geo-api-backend-base:latest

WORKDIR /app/

COPY ./app /app
ENV PYTHONPATH=/app
CMD ["/app/start.sh"]