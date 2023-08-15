FROM tiangolo/uvicorn-gunicorn:python3.11
LABEL maintainer="Sebastian Ramirez <tiangolo@gmail.com>"
WORKDIR /logica_api
COPY pyproject.toml /logica_api
COPY . /logica_api
RUN pip install --no-cache-dir poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction --no-ansi
EXPOSE 8888