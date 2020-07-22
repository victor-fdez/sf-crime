import argparse

from confluent_kafka import Consumer

def feed(args):
    consumer_conf = {'bootstrap.servers': args.bootstrap_servers,
                     'group.id': 0,
                     'auto.offset.reset': "earliest"}
    
    consumer = Consumer(consumer_conf)
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
    feed(parser.parse_args())
