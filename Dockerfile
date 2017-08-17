FROM centos:7
MAINTAINER Edward Gomez <egomez@lco.global>

EXPOSE 80
ENTRYPOINT [ "/init" ]

# Setup the Python Django environment
ENV PYTHONPATH /var/www/serol
ENV DJANGO_SETTINGS_MODULE serol.settings

# install and update packages
RUN yum -y install epel-release \
        && yum -y install postgresql96 python-pip nginx supervisor uwsgi-plugin-python \
        && yum -y update \
        && yum -y clean all

# install python requirements
COPY requirements.pip /var/www/serol/requirements.pip
RUN pip install --upgrade pip \
        && pip install -r /var/www/serol/requirements.pip \
        && rm -rf /root/.cache /root/.pip

# install configuration
COPY docker/processes.ini /etc/supervisord.d/
COPY docker/nginx/* /etc/nginx/
COPY docker/uwsgi.ini /etc/
COPY docker/init /init

# install webapp
COPY . /var/www/serol
