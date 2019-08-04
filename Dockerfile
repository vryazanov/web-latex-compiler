FROM python:3.6

RUN apt-get update -y
RUN apt-get install -y texlive-full texlive

COPY . /app
WORKDIR /app

RUN pip install pipenv
RUN pipenv install --system --dev
