FROM python:3.9-alpine

WORKDIR /app

# install depedencies
COPY requirements.txt .
RUN apk --no-cache add \
            libgomp \
            libjpeg-turbo \
            postgresql-libs \
            openblas \
            zlib \
            python3-dev \
            libffi-dev \
        && apk --no-cache add --virtual .build-deps \
            g++ \
            gcc \
            git \
            make \
            libjpeg-turbo-dev \
            postgresql-dev \
            musl-dev \
            openblas-dev \
            zlib-dev \
        && pip --no-cache-dir --trusted-host=buildsba.lco.gtn install -r requirements.txt \
        && apk --no-cache del .build-deps

# install web application
COPY app/ .
