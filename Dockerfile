FROM mundialis/esa-snap:ubuntu
RUN apt-get update && apt-get install -y bash python-gdal python3-gdal gdal-bin krb5-user sssd-tools openjdk-8-jre-headless && rm -rf /var/cache/apt/*
RUN mkdir /etc/krb5.conf.d
RUN pip3.6 install Fiona pandas==1.0.0 pyproj python_dateutil pytz Shapely progressbar2 numpy spatialist>=0.9 pyyaml requests psycopg2==2.7.7 SQLAlchemy>=1.4 SQLAlchemy-Utils>=0.37 GeoAlchemy2 geopandas pyroSAR && rm -rf /root/.cache/pip/
ENV JAVA_HOME "/usr/lib/jvm/java-8-openjdk-amd64/"
ENV PATH="${PATH}:/usr/local/snap/bin"
ENTRYPOINT []
