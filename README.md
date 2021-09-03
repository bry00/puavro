# puavro

The `puavro` is a small convenience library enabling usage of the [Apache Pulsar Python client](https://pulsar.apache.org/docs/en/client-libraries-python/)
with pre-defined [AVRO schemas]((https://avro.apache.org/docs/current/spec.html)) and
[Python dictionaries](https://docs.python.org/3/tutorial/datastructures.html#dictionaries) instead of [AVRO schemas declared as records](https://pulsar.apache.org/docs/en/client-libraries-python/#declare-and-validate-schema).

In other words, the library provides an interface to the standard Apache Pulsar client
allowing to read/write AVRO messages from/to Python dictionary using AVRO schema, either:

- declared as Python dictionary (using [`fastavro.schema.parse_schema()`](https://fastavro.readthedocs.io/en/latest/schema.html#fastavro._schema_py.parse_schema)) or
- loaded from .avsc file (using [`fastavro.schema.load_schema()`](https://fastavro.readthedocs.io/en/latest/schema.html#fastavro._schema_py.load_schema)) or
- parsed from JSON string (using `fastavro.schema.parse_schema(json.loads())`).

The `puavro` library consists of just two classes:

- `DictAVRO` derived from Python [`dict`](https://docs.python.org/3/library/stdtypes.html#dict) and designated to be used instead of `pulsar.schema.Record` class;
- `DictAvroSchema` derived from `pulsar.schema.AvroSchema` and designated to be used instead.

See also:

  - [How to use](#how-to-use)
  - [Samples](#samples)

## Motivation

To enable usage of Python Pulsar client with AVRO messages generated / received by modules written in other languages and using external AVRO schemas (e.g. stored in .avsc files).

## Installing

`puavro` is available on PyPi:

```console
pip install puavro
```

## Dependencies

The library depends on the following modules:

```python
fastavro>=1.4.4
pulsar-client>=2.7.0
```

## Compatibility

The library has been run and tested against [Pulsar Python client](https://pulsar.apache.org/docs/en/client-libraries-python) v. 2.7.0 and 2.8.0. and
[fastavro](https://github.com/fastavro/fastavro) v. 1.4.4. and is expected to be compatible with all higher versions also.

## License

The library is provided under terms of the [MIT license](LICENSE).

## How to use

The samples in this sections assume the following imports:

```python
import pulsar
import fastavro
import puavro

import json
import datetime
from pprint import pp
```

### Defining dictionary for AVRO schema

```Python
class Segment(puavro.DictAVRO):
    SCHEMA = fastavro.schema.load_schema("Segment.avsc")
```

or

```Python
class Segment(puavro.DictAVRO):
    SCHEMA = fastavro.schema.parse_schema(json.loads("""{
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
```

or 

```python
class Segment(puavro.DictAVRO):
    SCHEMA = fastavro.schema.parse_schema({
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
        })
```

or

```python
class Segment(puavro.DictAVRO):
    pass

Segment.set_schema(fastavro.schema.load_schema("segment.avsc"))
```

### Producer

Using class `Segment` (derived from `puavro.DictAVRO` above) and `puavro.DictAvroSchema` class (instead of `pulsar.schema.AvroSchema`):

```python
PULSAR_SERVICE_URL = "pulsar://localhost:6650"
TOPIC = "try"

pulsar_client = pulsar.Client(PULSAR_SERVICE_URL)
producer = pulsar_client.create_producer(topic=TOPIC, 
                                         schema=puavro.DictAvroSchema(Segment))
try:
    segment = Segment(
        id=99,
        name = "some name",
        when = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc),
        direction = "north",
        length = 12345,
    )
    producer.send(segment)
finally:
    producer.close()
    pulsar_client.close()
```

### Consumer

Using class `Segment` (derived from `puavro.DictAVRO` above) and `puavro.DictAvroSchema` class (instead of `pulsar.schema.AvroSchema`):

```python
PULSAR_SERVICE_URL = "pulsar://localhost:6650"
TOPIC = "try"
WAIT_SECONDS = 3

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
```

## Samples

The complete samples can be found in the [samples](samples) directory:

- Producer: [sender.py](samples/sender.py)
- Consumer: [receiver.py](samples/sender.py)
- AVRO schema: [Segment.avsc](samples/Segment.avsc)
- AVRO IDL: [try.avdl](samples/try.avdl)
