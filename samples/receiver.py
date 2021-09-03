#!/usr/bin/env python3

import sys
import os
from pprint import pp

import pulsar
import fastavro
import puavro

PULSAR_SERVICE_URL = "pulsar://localhost:6650"
TOPIC = "try"
WAIT_SECONDS = 3


class Segment(puavro.DictAVRO):
    SCHEMA = fastavro.schema.load_schema(os.path.join(os.path.realpath(os.path.dirname(sys.argv[0])), "Segment.avsc"))


pulsar_client = pulsar.Client(PULSAR_SERVICE_URL)
consumer = pulsar_client.subscribe(TOPIC,
                                   subscription_name="sample",
                                   consumer_type=pulsar.ConsumerType.Shared,
                                   schema=puavro.DictAvroSchema(Segment))
try:
    while True:
        msg = consumer.receive(WAIT_SECONDS * 1000)
        segment = msg.value()

        pp(segment)

        consumer.acknowledge(msg)
except Exception as e:
    if str(e) == 'Pulsar error: TimeOut':
        print("END OF DATA")
    else:
        raise
finally:
    consumer.close()
    pulsar_client.close()
