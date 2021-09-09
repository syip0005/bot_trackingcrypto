import json

with open('sample_payload.json') as f:

    data = json.load(f)

print(type(data))