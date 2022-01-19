# syntax=docker/dockerfile:1

FROM mundialis/esa-snap:ubuntu

RUN rm /etc/apt/sources.list
COPY ./sources.list /etc/apt/sources.list
RUN apt-get update && apt-get install bash
RUN apt-get install -y python-gdal python3-gdal gdal-bin