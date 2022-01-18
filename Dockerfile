# syntax=docker/dockerfile:1

FROM mundialis/esa-snap:ubuntu
RUN apt-get update && apt-get install -y bash
RUN apt-get install -y python-gdal python3-gdal gdal-bin