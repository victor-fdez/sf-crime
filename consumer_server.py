import argparse

from confluent_kafka import DeserializingConsumer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer
from confluent_kafka.serialization import StringDeserializer


def feed(args):
    schema_str = args.avro_definition.read()

    schema_registry_conf = {'url': args.schema_registry}
    schema_registry_client = SchemaRegistryClient(schema_registry_conf)

    avro_serializer = AvroDeserializer(schema_str,
                                       schema_registry_client)

    consumer_conf = {'bootstrap.servers': args.bootstrap_servers,
                     'key.deserializer': StringDeserializer(codec='utf_8'),
                     'value.deserializer': avro_serializer,
                     'group.id': 0,
                     'auto.offset.reset': "earliest"}
    
    consumer = DeserializingConsumer(consumer_conf)
    consumer.subscribe([args.topic])

    while True:
        try:
            msg = consumer.poll(0.5)
            if msg is None:
                continue

            crime = msg.value()
            if crime is not None:
                print(crime)
        except KeyboardInterrupt:
            break

    consumer.close()



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Producer JSON")
    parser.add_argument('-b', dest="bootstrap_servers", required=False, default="kafka0:9093",
                        help="Bootstrap broker(s) (host[:port])")
    parser.add_argument('-s', dest="schema_registry", required=False, default="http://schema-registry:8081",
                        help="Schema Registry (http(s)://host[:port]")
    parser.add_argument('-t', dest="topic", required=True,
                        help="Topic name")
    parser.add_argument('avro_definition', type=argparse.FileType('r'),
                        help="Avro File Definition")
    feed(parser.parse_args())
