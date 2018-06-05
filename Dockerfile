FROM python:3.6-alpine
MAINTAINER Edward Gomez <egomez@lco.global>

ENV PYTHONUNBUFFERED 1
ENV C_FORCE_ROOT true

# install depedencies
COPY requirements.pip /var/www/apps/serol/
RUN apk --no-cache add postgresql-libs \
        && apk --no-cache add --virtual .build-deps gcc git musl-dev postgresql-dev \
        && apk --no-cache add libjpeg-turbo jpeg-dev libjpeg libjpeg-turbo-dev imagemagick zlib zlib-dev \
        && pip --no-cache-dir --trusted-host=buildsba.lco.gtn install -r /var/www/apps/serol/requirements.pip \
        && apk --no-cache del .build-deps

# install entrypoint
COPY docker/init /

# install web application
COPY app /var/www/apps/serol/
ENTRYPOINT [ "/init" ]
