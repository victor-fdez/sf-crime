import faust
import json
import fastavro

app = faust.App('Crime', broker='kafka://kafka0:9093')

avro_schema = ''
with open('producer_server/police-department-calls-for-service-schema.json') as f:
  avro_schema = json.load(f)

def fast_avro_decode(schema, encoded_message):
    stringio = io.BytesIO(encoded_message)
    return fastavro.schemaless_reader(stringio, schema)

topic = app.topic('crime_data', value_type=bytes)

def fast_avro_decode(schema, encoded_message):
    stringio = io.BytesIO(encoded_message)
    return fastavro.schemaless_reader(stringio, schema)

@app.agent(topic)
async def crimes(records):
    async for record in records:
        schema = fastavro.parse_schema(avro_schema)
        fast_avro_decode(schema, record) 
        # process infinite stream of orders.
        print(f'Crime {crime}')

if __name__ == '__main__':
    app.main()