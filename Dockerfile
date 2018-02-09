FROM centos:7
MAINTAINER Edward Gomez <egomez@lco.global>

EXPOSE 80
ENTRYPOINT [ "/init" ]

# Setup the Python Django environment
ENV PYTHONPATH /var/www/serol
ENV DJANGO_SETTINGS_MODULE serol.settings

# install and update packages
RUN yum -y install epel-release \
        && yum -y install cronie postgresql96 python-pip nginx supervisor uwsgi-plugin-python \
        && yum -y install libjpeg-devel ImageMagick \
        && yum -y install 'http://www.astromatic.net/download/stiff/stiff-2.4.0-1.x86_64.rpm' \
        && yum -y install 'http://www.astromatic.net/download/sextractor/sextractor-2.19.5-1.x86_64.rpm' \
        && yum -y update \
        && yum -y clean all

# install python requirements
COPY requirements.pip /var/www/serol/requirements.pip
RUN pip install --upgrade pip \
        && pip install -r /var/www/serol/requirements.pip \
        && rm -rf /root/.cache /root/.pip

# Ensure crond will run on all host operating systems
RUN sed -i -e 's/\(session\s*required\s*pam_loginuid.so\)/#\1/' /etc/pam.d/crond

# install configuration
COPY docker/ /

# install webapp
COPY . /var/www/serol
