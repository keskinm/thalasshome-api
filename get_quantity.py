
from google.cloud import datastore

datastore_client = datastore.Client()

def print_quantity():
    key = datastore_client.key("Task", "sampletask1")
    task = datastore_client.get(key)
    print("quantity:", task)

print_quantity()
