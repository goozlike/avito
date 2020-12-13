FROM python:3.8

RUN mkdir /app/
WORKDIR /app/
COPY requirements.txt .
COPY test.py .
COPY client.py .
COPY transport.py .

RUN pip install -r requirements.txt

COPY . .
ENTRYPOINT ["pytest", "test.py", "-vs"]
