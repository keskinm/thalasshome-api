
from google.cloud import datastore

datastore_client = datastore.Client()

def print_hardcode_updated_order():
    key = datastore_client.key("orders", 3662977106104)
    print("key", key)
    order = datastore_client.get(key)
    print("order", order)

print_hardcode_updated_order()
