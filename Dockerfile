FROM python:3.11-slim

WORKDIR /usr/src/app

COPY requirements.txt .
RUN pip install -r requirements.txt
COPY ./app .

CMD ["python", "app.py"]

EXPOSE 5000