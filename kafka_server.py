import argparse

from confluent_kafka.serialization import StringSerializer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer

import producer_server

def run_kafka_server(args):
    schema_str = args.avro_definition.read()

    schema_registry_conf = {'url': args.schema_registry}
    schema_registry_client = SchemaRegistryClient(schema_registry_conf)

    avro_serializer = AvroSerializer(schema_str,
                                     schema_registry_client,
                                     to_dict=lambda x, sr : vars(x))

    producer_conf = {'bootstrap.servers': args.bootstrap_servers,
                     'key.serializer': StringSerializer(codec='utf_8'),
                     'value.serializer': avro_serializer,
                     'schema': schema_str}

    producer = producer_server.ProducerServer(producer_conf)

    return producer


def feed(args):
    producer = run_kafka_server(args)
    producer.generate_data(input_file=args.json_data, topic_name=args.topic)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Producer JSON")
    parser.add_argument('-b', dest="bootstrap_servers", required=False, default="kafka0:9092",
                        help="Bootstrap broker(s) (host[:port])")
    parser.add_argument('-s', dest="schema_registry", required=False, default="http://schema-registry:8081",
                        help="Schema Registry (http(s)://host[:port]")
    parser.add_argument('-t', dest="topic", required=True,
                        help="Topic name")
    parser.add_argument('avro_definition', type=argparse.FileType('r'),
                        help="Avro File Definition")
    parser.add_argument('json_data', type=argparse.FileType('r'),
                        help="JSON file containing all data to produce to Kafka")
    feed(parser.parse_args())
