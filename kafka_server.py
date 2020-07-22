import argparse

from confluent_kafka.serialization import StringSerializer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer

import producer_server

def run_kafka_server(args):
    producer_conf = {'bootstrap.servers': args.bootstrap_servers}

    producer = producer_server.ProducerServer(producer_conf)

    return producer


def feed(args):
    producer = run_kafka_server(args)
    producer.generate_data(input_file=args.json_data, topic_name=args.topic)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Producer JSON")
    parser.add_argument('-b', dest="bootstrap_servers", required=False, default="kafka0:9093",
                        help="Bootstrap broker(s) (host[:port])")
    parser.add_argument('-t', dest="topic", required=True,
                        help="Topic name")
    parser.add_argument('json_data', type=argparse.FileType('r'),
                        help="JSON file containing all data to produce to Kafka")
    feed(parser.parse_args())
