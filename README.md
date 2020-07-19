# San Francisco Crime

## Running Project

### Start Kafka & Zookeeper Services

```
docker-compose up -d kafka0 zookeeper
```

### Start Producer to upload AVRO records to Kafka

```
docker-compose run --rm producer python kafka_server.py -t crime_data -b kafka0:9093 ./producer_server/police-department-calls-for-service-schema.json police-department-calls-for-service.json
```

### Start Consumer to download AVRO records



## Picture Submissiones

### Picture 1 - Take a screenshot of your kafka-consumer-console output. You will need to include this screenshot as part of your project submission.

![](images/consumer_logs.png)

### Picture 2 - Take a screenshot of your progress reporter after executing a Spark job.

### Picture 3 - Take a screenshot of the Spark Streaming UI as the streaming continues.

## Respones

### How did changing values on the SparkSession property parameters affect the throughput and latency of the data?

### What were the 2-3 most efficient SparkSession property key/value pairs? Through testing multiple variations on values, how can you tell these were the most optimal?

