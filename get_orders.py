
from google.cloud import datastore

datastore_client = datastore.Client()

def print_hardcode_updated_order():
    key = datastore_client.key("Orders", "harcoded_id_01")
    task = datastore_client.get(key)
    print("order", task)


def print_created_order_sample():
    key = datastore_client.key("Orders", "RECEIVED_WEBHOOK")
    task = datastore_client.get(key)
    print("received_webhook", task)


print_hardcode_updated_order()
print_created_order_sample()
