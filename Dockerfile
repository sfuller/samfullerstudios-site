FROM ubuntu:20.04

RUN apt-get update
RUN apt-get install -y python3.8 python3-pip
RUN apt-get install -y npm

RUN mkdir /django
WORKDIR /django

ADD requirements.txt .
RUN python3.6 -m pip install -r requirements.txt

ADD samfullerstudios samfullerstudios
ADD sfs_site sfs_site
ADD manage.py .

WORKDIR /django/sfs_site/static
RUN npm install materialize-css@1.0
RUN npm install jquery@3.5
RUN apt-get purge -y npm
RUN apt-get autoremove -y

WORKDIR /django
RUN SFS_DEBUG=true python3.8 manage.py collectstatic
CMD python3.8 manage.py migrate && gunicorn samfullerstudios.wsgi -b 0.0.0.0:80
