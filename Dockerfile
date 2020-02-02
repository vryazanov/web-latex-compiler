
FROM python:3.7 as web
COPY . /app
WORKDIR /app
RUN pip install pipenv
RUN pipenv install --system
CMD ["./scripts/web.sh"]

FROM python:3.7 as base_worker
RUN apt-get update -y
RUN apt-get install -y texlive-full texlive

FROM base_worker as tests
COPY . /app
WORKDIR /app
RUN pip install pipenv
RUN pipenv install --system --dev

FROM base_worker as worker
COPY . /app
WORKDIR /app
RUN pip install pipenv
RUN pipenv install --system
ENTRYPOINT ["./scripts/worker.sh"]
