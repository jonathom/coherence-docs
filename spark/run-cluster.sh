#!/bin/sh

export PYSPARK_PYTHON=/usr/bin/python3.6

zip -r histogram.zip histogram/

spark-submit --master yarn --deploy-mode=cluster \
--conf spark.yarn.appMasterEnv.YARN_CONTAINER_RUNTIME_DOCKER_MOUNTS=/var/lib/sss/pipes:/var/lib/sss/pipes:rw,/usr/hdp/current/:/usr/hdp/current/:ro,/etc/hadoop/conf/:/etc/hadoop/conf/:ro,/etc/krb5.conf:/etc/krb5.conf:ro \
--conf spark.yarn.appMasterEnv.YARN_CONTAINER_RUNTIME_TYPE=docker \
--conf spark.yarn.appMasterEnv.YARN_CONTAINER_RUNTIME_DOCKER_IMAGE=vito-docker-private.artifactory.vgt.vito.be/dockerspark-quickstart \
--conf spark.executorEnv.YARN_CONTAINER_RUNTIME_TYPE=docker \
--conf spark.executorEnv.YARN_CONTAINER_RUNTIME_DOCKER_IMAGE=vito-docker-private.artifactory.vgt.vito.be/dockerspark-quickstart \
--conf spark.executorEnv.YARN_CONTAINER_RUNTIME_DOCKER_MOUNTS=/var/lib/sss/pipes:/var/lib/sss/pipes:rw,/usr/hdp/current/:/usr/hdp/current/:ro,/etc/hadoop/conf/:/etc/hadoop/conf/:ro,/etc/krb5.conf:/etc/krb5.conf:ro,/data/MTDA/TIFFDERIVED/PROBAV_L3_S1_TOC_333M:/data/MTDA/TIFFDERIVED/PROBAV_L3_S1_TOC_333M:ro,/home/jonathanbahlmann/Public:/home/jonathanbahlmann/Public:rw \
--conf spark.shuffle.service.enabled=true --conf spark.dynamicAllocation.enabled=true \
--py-files histogram.zip spark.py

# /data/MTDA/CGS_S1/CGS_S1_SLC_L1/IW/DV:/data/MTDA/CGS_S1/CGS_S1_SLC_L1/IW/DV:ro