FROM python:3.8

RUN mkdir /app/
WORKDIR /app/
COPY ttl_cache.py .
COPY transport.py .

COPY . .
EXPOSE 8081
CMD ["python", "server.py"]