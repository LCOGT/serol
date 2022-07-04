FROM python:3.9-slim-buster
WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN buildDeps='gcc g++' && \
    apt-get update && \
    apt-get install $buildDeps --no-install-recommends -y \
    gettext python3-cffi libcairo2 libpango-1.0-0 \
    libjpeg62-turbo-dev zlib1g-dev \
    postgresql-11 libpq-dev \
    libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info -y \
    && python3 -m pip install -r requirements.txt \
    && apt-get purge $buildDeps -y \
    && apt-get purge $(aptitude search '~i!~M!~prequired!~pimportant!~R~prequired!~R~R~prequired!~R~pimportant!~R~R~pimportant!busybox!grub!initramfs-tools' | awk '{print $2}') -y \
    && apt-get purge aptitude -y \
    && apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

COPY . /app
