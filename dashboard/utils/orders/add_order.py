from google.cloud import datastore

from dashboard.utils.samples.orders.orders import orders
datastore_client = datastore.Client()


def add_order_samples(orders):
    kind = "orders"

    for order in orders:
        name = order['id']
        key = datastore_client.key(kind, name)
        c_order = datastore.Entity(key=key)
        for k, v in order.items():
            c_order[k] = v
        datastore_client.put(c_order)


add_order_samples(orders)
