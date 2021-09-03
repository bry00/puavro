#!/usr/bin/env python3
import sys
import os
import datetime
import random
from pprint import pformat

import pulsar
import fastavro
import puavro

PULSAR_SERVICE_URL = "pulsar://localhost:6650"
TOPIC = "try"


class Segment(puavro.DictAVRO):
    SCHEMA = fastavro.schema.load_schema(os.path.join(os.path.realpath(os.path.dirname(sys.argv[0])), "Segment.avsc"))


if __name__ == '__main__':
    pulsar_client = pulsar.Client(PULSAR_SERVICE_URL)
    producer = pulsar_client.create_producer(topic=TOPIC,
                                             schema=puavro.DictAvroSchema(Segment))
    try:
        segment = Segment(
            id=random.randint(1, 10000),
            name = ["Full Ahead", "Half Ahead", "Slow Ahead", "Dead Slow Ahead"][random.randint(0, 3)],
            when = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc),
            direction = ["north", "east", "south", "west"][random.randint(0, 3)],
            length = random.randint(1, 10000),
        )
        producer.send(segment)
        print("Sent:\n{}".format(pformat(segment, indent=4, sort_dicts=False)))
    finally:
        producer.close()
        pulsar_client.close()
