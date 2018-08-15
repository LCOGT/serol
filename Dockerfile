FROM python:3.6-alpine
MAINTAINER Edward Gomez <egomez@lco.global>

ENTRYPOINT [ "/init" ]

# install depedencies
COPY requirements.pip /var/www/apps/serol/
RUN apk --no-cache add dcron libjpeg-turbo mariadb-connector-c nginx openblas supervisor zlib \
        && apk --no-cache add --virtual .build-deps gcc g++ git \
                libjpeg-turbo-dev mariadb-dev musl-dev openblas-dev zlib-dev \
        && pip --no-cache-dir --trusted-host=buildsba.lco.gtn install -r /var/www/apps/serol/requirements.pip \
        && apk --no-cache del .build-deps

# install entrypoint
COPY docker/ /

# install web application
COPY app /var/www/apps/serol/
