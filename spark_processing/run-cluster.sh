#!/bin/sh

export PYSPARK_PYTHON=/usr/bin/python3.6

zip -r worker_node.zip worker_node/

spark-submit --master yarn --deploy-mode=cluster \
--conf spark.yarn.appMasterEnv.YARN_CONTAINER_RUNTIME_DOCKER_MOUNTS=/var/lib/sss/pipes:/var/lib/sss/pipes:rw,/usr/hdp/current/:/usr/hdp/current/:ro,/etc/hadoop/conf/:/etc/hadoop/conf/:ro,/etc/krb5.conf:/etc/krb5.conf:ro,/var/lib/sss/pubconf/krb5.include.d:/var/lib/sss/pubconf/krb5.include.d:ro,/data/users/Public/jonathanbahlmann:/data/users/Public/jonathanbahlmann:rw \
--conf spark.yarn.appMasterEnv.YARN_CONTAINER_RUNTIME_TYPE=docker \
--conf spark.yarn.appMasterEnv.YARN_CONTAINER_RUNTIME_DOCKER_IMAGE=vito-docker.artifactory.vgt.vito.be/esa-snap-gdal:0.0.8 \
--conf spark.executorEnv.YARN_CONTAINER_RUNTIME_TYPE=docker \
--conf spark.executorEnv.YARN_CONTAINER_RUNTIME_DOCKER_IMAGE=vito-docker.artifactory.vgt.vito.be/esa-snap-gdal:0.0.8 \
--conf spark.executorEnv.YARN_CONTAINER_RUNTIME_DOCKER_MOUNTS=/var/lib/sss/pipes:/var/lib/sss/pipes:rw,/usr/hdp/current/:/usr/hdp/current/:ro,/etc/hadoop/conf/:/etc/hadoop/conf/:ro,/etc/krb5.conf:/etc/krb5.conf:ro,/data/MTDA/CGS_S1/CGS_S1_SLC_L1/IW/DV:/data/MTDA/CGS_S1/CGS_S1_SLC_L1/IW/DV:ro,/data/users/Public/jonathanbahlmann:/data/users/Public/jonathanbahlmann:rw \
--conf spark.shuffle.service.enabled=true --conf spark.dynamicAllocation.enabled=true \
--conf spark.executorEnv.HOME=/data/users/Public/jonathanbahlmann \
--conf spark.yarn.executor.memoryOverhead=8G \
--py-files worker_node.zip spark.py