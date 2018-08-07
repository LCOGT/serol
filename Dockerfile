FROM python:3.6-alpine
MAINTAINER Edward Gomez <egomez@lco.global>

ENV PYTHONUNBUFFERED 1
ENV C_FORCE_ROOT true

# install depedencies
COPY requirements.pip /var/www/apps/serol/
RUN apk --no-cache add --virtual .build-deps gcc g++ git mariadb-dev musl-dev \
        && apk --no-cache add libjpeg-turbo jpeg-dev libjpeg libjpeg-turbo-dev imagemagick zlib zlib-dev \
        && apk --no-cache add lapack openblas-dev openblas \
        && pip --no-cache-dir --trusted-host=buildsba.lco.gtn install -r /var/www/apps/serol/requirements.pip \
        && apk --no-cache del .build-deps \
        && apk add --no-cache mariadb-client-libs

# install entrypoint
COPY docker/init /

# install web application
COPY app /var/www/apps/serol/
ENTRYPOINT [ "/init" ]
