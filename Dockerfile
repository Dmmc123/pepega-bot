# telegram bot app
FROM python:3.9 AS python

COPY requirements.txt /bot/requirements.txt
WORKDIR /bot
RUN pip install -r requirements.txt
COPY . /bot

CMD ["python", "main.py"]
