import os
from cloudflare import Cloudflare
import json

client = Cloudflare(
    api_email="MY_API_EMAIL",
    api_key="MY_API_KEY"
)

kv_pairs = []
with open("tokens.json", "r") as file:
    for key in json.load(file):
        kv_pairs.append({
            "key": key,
            "value": "0"
        })

# Documentation is wrong, namespaces has no "keys" member
response = client.kv.namespaces.bulk_update(
    namespace_id="MY_NAMESPACE_ID",
    account_id="MY_ACCOUNT_ID",
    body=kv_pairs
)

print(response)