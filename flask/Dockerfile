FROM python:3.10.16

RUN apt-get update -y && apt-get upgrade -y &&\
  apt-get install tree sqlite3 -y &&\
  apt-get autoremove -y &&\
  apt-get clean &&\
  rm -rf /usr/local/src/*

COPY requirements.txt requirements.txt
RUN pip install -U pip &&\
  pip install --no-cache-dir -r requirements.txt 