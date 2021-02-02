FROM ubuntu:20.04

RUN apt-get update
RUN apt-get install -y python3.8 python3-pip

RUN mkdir /django
WORKDIR /django

ADD requirements.txt .
RUN python3.8 -m pip install -r requirements.txt

ADD samfullerstudios samfullerstudios
ADD sfs_site sfs_site
ADD manage.py .

# TODO: Pagebuilder will be a separate tool later
ADD pagebuilder.py .

WORKDIR /django
RUN SFS_DEBUG=true python3.8 manage.py collectstatic
CMD python3.8 manage.py migrate && gunicorn samfullerstudios.wsgi -b 0.0.0.0:80
