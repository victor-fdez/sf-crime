import time
from uuid import uuid4
import pprint
import pdb
import json

import ijson
from confluent_kafka import Producer

class obj(object):
    def __init__(self, d):
        for a, b in d.items():
            if isinstance(b, (list, tuple)):
               setattr(self, a, [obj(x) if isinstance(x, dict) else x for x in b])
            else:
               setattr(self, a, obj(b) if isinstance(b, dict) else b)

def delivery_report(err, msg):
    """
    Reports the failure or success of a message delivery.
    Args:
        err (KafkaError): The error that occurred on None on success.
        msg (Message): The message that was produced or failed.
    Note:
        In the delivery report callback the Message.key() and Message.value()
        will be the binary format as encoded by any configured Serializers and
        not the same object that was passed to produce().
        If you wish to pass the original object(s) for key and value to delivery
        report callback we recommend a bound callback or lambda where you pass
        the objects along.
    """
    if err is not None:
        print("Delivery failed for User record {}: {}".format(msg.key(), err))
        return
    print('User record {} successfully produced to {} [{}] at offset {}'.format(
        msg.key(), msg.topic(), msg.partition(), msg.offset()))

class ProducerServer(Producer):

    def __init__(self, kwargs):
        super().__init__(kwargs)

    def generate_data(self, topic_name, input_file):
        for jvalue in ijson.items(input_file, 'item'):
            self.poll(0)
            #message = self.dict_to_binary(obj)
            key = str(uuid4())
            #pdb.set_trace()
            value = json.dumps(jvalue)
            pp = pprint.PrettyPrinter(indent=4)
            pp.pprint(key)
            pp.pprint(value)
            # Send data to Kafka
            self.produce(topic_name, key=key, value=value, on_delivery=delivery_report)
            self.flush()
            #time.sleep(0.1)

    # TODO fill this in to return the json dictionary to binary
    def dict_to_binary(self, json_dict):
        return 
        