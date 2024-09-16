FROM python:3.10.14-slim-bullseye

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir requests python-dotenv

CMD ["python", "init.py"]