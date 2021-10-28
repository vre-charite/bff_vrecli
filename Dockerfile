FROM python:3.7-buster
USER root
WORKDIR /usr/src/app

RUN apt-get update
RUN apt-get install -y vim less
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt --proxy="http://proxy.charite.de:8080/"
COPY . .
CMD ["./gunicorn_starter.sh"]
