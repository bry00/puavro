import io

import pulsar
import fastavro


class DictAVRO(dict):
    """``DictAVRO`` provides dictionary class compatible with the Pulsar AVRO "record" interface.
    The class is based on regular Python dictionary (``dict``).

    The actual "record" classes should be based on the ``DictAVRO`` and either:

    - set ``SCHEMA`` class variable to the parsed AVRO schema,
    - use ``set_schema`` class method to set parsed AVRO schema.
    """

    _schema = None

    @classmethod
    def schema(cls) -> str:
        """Class method providing AVRO schema related to the class.

       Returns:
            AVRO schema associated with the class.
        """
        if cls._schema is None:
            if hasattr(cls, "SCHEMA") and not cls.SCHEMA is None:
                cls._schema = cls.SCHEMA
        if cls._schema is None:
            raise ValueError(
                "AVRO schema (e.g. from fastavro.schema.load_schema()) must be provided as SCHEMA attribute")
        return cls._schema

    @classmethod
    def set_schema(cls, schema: str):
        """Sets AVRO schema  for all derived classes.

        Args:
            schema (str):  parsed AVRO schema
        """
        cls._schema = schema


class DictAvroSchema(pulsar.schema.AvroSchema):
    """``DictAvroSchema`` provides AVRO schema class compatible with the Pulsar AVRO interface.
    """

    def __init__(self, record_cls):
        """
        Args:
            record_cls (class): Class used as a record to write/read Pulsar AVRO messages.
                                Should be derived from :class:`DictAVRO`
        """
        if not issubclass(record_cls, DictAVRO):
            raise TypeError(
                'Invalid record type {} - record should be derived from DictAVRO class'.format(record_cls.__name__))
        super().__init__(record_cls)


    def encode(self, obj):
        """Encodes the given object. Used internally by the Pulsar client.
        Overrides base implementation in order to allow usage of ``DictAVRO`` based objects.

        Args:
            obj: AVRO record object to be encoded.
                 Should be the object of the same class that was used to
                 initialize the current instance of the class:`DictAVRO`,
                 i.e. class derivated from :class:`DictAVRO`.
        """
        self._validate_object_type(obj)
        buffer = io.BytesIO()
        fastavro.schemaless_writer(buffer, self._schema, obj)
        return buffer.getvalue()


if __name__ == '__main__':
    import sys
    import json
    import datetime
    import time
    from pprint import pp

    WAIT_SECONDS = 3
    PULSAR_SERVICE_URL = "pulsar://localhost:6650"
    TOPIC = "try"
    AVRO_SCHEMA = fastavro.schema.load_schema(sys.argv[1]) if len(sys.argv) > 1 else fastavro.schema.parse_schema(json.loads(
        """{
  "type" : "record",
  "name" : "Segment",
  "namespace" : "try",
  "fields" : [ {
    "name" : "id",
    "type" : "long"
  }, {
    "name" : "name",
    "type" : "string"
  }, {
    "name" : "when",
    "type" : {
      "type" : "long",
      "logicalType" : "timestamp-millis"
    }
  }, {
    "name" : "direction",
    "type" : {
      "type" : "enum",
      "name" : "CardinalDirection",
      "symbols" : [ "north", "south", "east", "west" ]
    }
  }, {
    "name" : "length",
    "type" : [ "null", "long" ]
  } ]
}
"""))


    def send():
        class Segment(DictAVRO):
            SCHEMA = AVRO_SCHEMA

        pulsar_client = pulsar.Client(PULSAR_SERVICE_URL)
        producer = pulsar_client.create_producer(topic=TOPIC, schema=DictAvroSchema(Segment))
        try:
            segment = Segment(
                id=99,
                name = "some name",
                when = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc),

            direction = "north",
                length = 12345,
            )
            producer.send(segment)
            pp(segment)
        finally:
            producer.close()
            pulsar_client.close()

    def receive():
        class Segment(DictAVRO):
            pass

        Segment.set_schema(AVRO_SCHEMA)
        pulsar_client = pulsar.Client(PULSAR_SERVICE_URL)
        consumer = pulsar_client.subscribe(TOPIC, subscription_name="try", consumer_type=pulsar.ConsumerType.Shared,
                                           schema=DictAvroSchema(Segment))
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

    send()
    time.sleep(WAIT_SECONDS)
    receive()
