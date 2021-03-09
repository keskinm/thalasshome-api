
from google.cloud import datastore

datastore_client = datastore.Client()


def print_hardcode_updated_order():
    key = datastore_client.key("orders", 3662977106104)
    print("key", key)
    order = datastore_client.get(key)
    print("order", order)


print_hardcode_updated_order()


def retrieve_all_entities(kind="orders"):
    query = datastore.Client().query(kind=kind)
    all_keys = query.fetch() #fetches all the entities from the datastore
    d = list(all_keys)
    print(d)

# retrieve_all_entities()
