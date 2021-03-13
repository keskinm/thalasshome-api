from google.cloud import datastore
datastore_client = datastore.Client()


def delete_all_orders(kind="orders"):
    query = datastore_client.query(kind=kind)
    all_entities = list(query.fetch())
    for entitiy in all_entities:
        key = entitiy.key
        datastore_client.delete(key)


delete_all_orders()

