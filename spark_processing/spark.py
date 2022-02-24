"""
This sample program uses Apache Spark to calculate a histogram for each PROBA-V tile within a given time range and
bounding box and sums them up - all in parallel.
"""

from datetime import datetime
from operator import add
from worker_node.files import processing_geojson_as_array
from worker_node.do_pyroSAR import do_pyroSAR

from pyspark import SparkContext
import geopandas as gpd

"""
The code in the __main__ block will be executed on a single node, the 'driver'. It describes the different steps that need
to be executed in parallel.
"""
if __name__ == '__main__':
    """
    Query the PROBA-V files that will be processed. This method returns a simple list of files that match a specific time range and bounding box.
    """
    
    # The SparkContext is our entry point to bootstrap parallel operations.
    sc = SparkContext(appName='python-spark-docker')
    
    # read processing.geojson and create a list of dataframes that need to be processed
    bursts_to_process = gpd.read_file("/data/users/Public/jonathanbahlmann/coherence-docs/preprocessing/processing.geojson")
    files = processing_geojson_as_array(bursts_to_process)

    try:
        # Distribute the local file list over the cluster. In Spark terminology, the result is called an RDD (Resilient Distributed Dataset).
        filesRDD = sc.parallelize(files) # TODO specify nr of partitions
        # Apply the 'do_pyroSAR' function to each gpdf using 'map', keep the result in memory using 'cache'.
        hists = filesRDD.map(do_pyroSAR).cache()
        print(type(hists))
        #Count number of histograms
        # count = hists.count()
        #Combine distributed histograms into a single result
        # total = list(hists.reduce(lambda h, i: map(add, h, i)))
        # total = hists.sum()

        print( "sum of rows: %s" % (hists.count()) )
    finally:
        sc.stop()
