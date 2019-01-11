FROM ubuntu:18.04

RUN apt-get update
RUN apt-get install -y python3.6 python3-pip
RUN apt-get install -y npm

RUN npm install -g bower
RUN apt-get install -y git

RUN mkdir /django
WORKDIR /django

ADD requirements.txt .
RUN python3.6 -m pip install -r requirements.txt

ADD samfullerstudios samfullerstudios
ADD sfs_site sfs_site
ADD manage.py .

WORKDIR /django/sfs_site/static
RUN bower update --allow-root
RUN apt-get purge -y git
RUN apt-get autoremove -y

WORKDIR /django
RUN SFS_DEBUG=true python3.6 manage.py collectstatic
CMD python3.6 manage.py migrate && gunicorn samfullerstudios.wsgi -b 0.0.0.0:80
