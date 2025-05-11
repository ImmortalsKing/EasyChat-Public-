FROM python:3.12

ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --timeout=1000 -r requirements.txt

COPY . .
COPY entrypoint.sh /entrypoint.sh

EXPOSE 8000

RUN chmod +x ./entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]
