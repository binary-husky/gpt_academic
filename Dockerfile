# syntax=docker/dockerfile:1

FROM python:3.10

ENV PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    PYTHONUNBUFFERED=1

RUN pip install "poetry==1.4"

WORKDIR /gpt

COPY poetry.lock pyproject.toml ./gpt/

RUN poetry install --no-dev --no--ansi

COPY . /gpt
RUN poetry install --no-dev

CMD ["chataca"]
