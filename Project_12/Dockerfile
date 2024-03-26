FROM ubuntu:18.04
ENV TZ=Europe/Moscow

ARG VERSION=0.0.1
LABEL "maintainer"="Mikhail Baranov <kinetikm@gmail.com>" \
      "app"="Abtester" \
      "version"="${VERSION}" 
      "description"="" \
      "tag"="alpha"

ADDED ./ /app
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN apt-get update
RUN apt-get install -y software-properties-common vim wget locales
RUN apt-get install -y build-essential python3-pip libpq-dev
RUN apt-get install git wget
    mkdir /logs

RUN sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && locale-gen
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

RUN python3 -m pip install pip --upgrade
RUN python3 -m pip install wheel

RUN python3 -m pip install -r /app/requirements.txt
RUN python3 /app/setup.py install

EXPORT ENV AB_CONFIG=/app/contrib/config.yml

WORKDIR /app
