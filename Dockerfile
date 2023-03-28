# syntax=docker/dockerfile:1
FROM python:3.10

ENV PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    PYTHONUNBUFFERED=1


RUN mkdir /gpt
COPY pyproject.toml ./gpt

WORKDIR /gpt
ENV PYTHONPATH=${PYTHONPATH}:${PWD}

RUN pip3 install poetry
RUN poetry install --no-dev

CMD ["chataca"]
