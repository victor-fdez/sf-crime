import time
from uuid import uuid4
import pprint
import pdb

import ijson
from confluent_kafka import SerializingProducer

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

class ProducerServer(SerializingProducer):

    def __init__(self, kwargs):
        self.schema_str = kwargs['schema']
        del kwargs['schema']
        super().__init__(kwargs)

    def generate_data(self, topic_name, input_file):
        int_fields = [a['name'] for a in ijson.items(self.schema_str,'fields.item') if a['type'] == 'int']
        for jvalue in ijson.items(input_file, 'item'):
            #message = self.dict_to_binary(obj)
            key = str(uuid4())
            jvalue = {k:(int(v) if k in int_fields else v) for k, v in jvalue.items()}
            #pdb.set_trace()
            value = obj(jvalue)
            pp = pprint.PrettyPrinter(indent=4)
            pp.pprint(key)
            pp.pprint(jvalue)
            #pp.pprint(self.len())
            #self.poll(0.0)
            self.produce(topic_name, key=key, value=value, on_delivery=delivery_report)
            self.flush()
            #self.send()
            time.sleep(1)

    # TODO fill this in to return the json dictionary to binary
    def dict_to_binary(self, json_dict):
        return 
        