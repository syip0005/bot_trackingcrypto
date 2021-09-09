import requests
import json

# Initialise webhook URL on localhost
webhook_url = 'http://18.223.158.215:5000/webhook'
webhook_url_local = 'http://localhost:5000/webhook'

# Load in sample data for testing
with open('./sample_payload.json', 'r') as f:
    data = json.load(f)

requests.post(webhook_url_local, json=json.dumps(data), headers={'Content-Type': 'application/json'}, verify=False)
