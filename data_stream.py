import logging
import json
from pyspark.sql import SparkSession
from pyspark.sql.types import *
from operator import add
import pyspark.sql.functions as psf


# TODO Create a schema for incoming resources
schema = StructType([
    StructField("crime_id", StringType(), False),
    StructField("original_crime_type_name", StringType(), True),
    StructField("report_date", StringType(), True),
    StructField("call_date", StringType(), True),
    StructField("offense_date", StringType(), True),
    StructField("call_time", StringType(), True),
    StructField("call_date_time", StringType(), True),
    StructField("disposition", StringType(), True),
    StructField("address", StringType(), True),
    StructField("city", StringType(), True),
    StructField("state", StringType(), True),
    StructField("agency_id", StringType(), False),
    StructField("address_type", StringType(), True),
    StructField("common_location", StringType(), True)
])

def run_spark_job(spark):

    # TODO Create Spark Configuration
    # Create Spark configurations with max offset of 200 per trigger
    # set up correct bootstrap server and port
    df = spark.readStream\
          .format("kafka")\
          .option("kafka.bootstrap.servers", "kafka0:9093")\
          .option("startingOffsets", "earliest")\
          .option("maxOffsetsPerTrigger", 500)\
          .option("subscribe","crime")\
          .load()

    # Show schema for the incoming resources for checks
    df.printSchema()

    # Take only value and convert it to String
    kafka_df = df.selectExpr("timestamp","CAST(value as STRING)")

    service_table = kafka_df\
        .select(kafka_df.timestamp, psf.from_json(psf.col('value'), schema).alias("DF"))\
        .select("timestamp","DF.*")

    service_table.createOrReplaceTempView("service_table")

    kafka_df.printSchema()
    service_table.printSchema()

    # select original_crime_type_name and disposition
    distinct_table = spark.sql("select timestamp, original_crime_type_name, disposition from service_table")

    # count the number of original crime type
    #agg_df = distinct_table.withWatermark("timestamp", "10 seconds").groupBy("original_crime_type_name",psf.window("timestamp", "5 seconds")).count()
    agg_df = distinct_table.withWatermark("timestamp", "10 seconds").groupBy("original_crime_type_name", "disposition").count()
    
    # Q1. Submit a screen shot of a batch ingestion of the aggregation
    # write output stream
    # query = agg_df.writeStream \
    #               .outputMode("complete")\
    #               .format("console")\
    #               .start()

    # attach a ProgressReporter
    # query.awaitTermination()

    # get the right radio code json path
    radio_code_json_filepath = "./radio_code.json"
    radio_code_df = spark.read.json(radio_code_json_filepath, multiLine=True)

    radio_code_df.printSchema()

    # clean up your data so that the column names match on radio_code_df and agg_df
    # we will want to join on the disposition code


    # rename disposition_code column to disposition
    radio_code_df = radio_code_df.withColumnRenamed("disposition_code", "disposition")

    # join on disposition column
    join_query = agg_df.join(radio_code_df, radio_code_df.disposition == agg_df.disposition, "inner")

    query = join_query.writeStream \
                    .outputMode("update")\
                    .format("console")\
                    .start()

    query.awaitTermination()


if __name__ == "__main__":
    logger = logging.getLogger(__name__)

    # TODO Create Spark in Standalone mode
    spark = SparkSession \
        .builder \
        .master("local[*]") \
        .appName("KafkaSparkStructuredStreaming") \
        .getOrCreate()

    logger.info("Spark started")

    run_spark_job(spark)

    spark.stop()
