from google.cloud import datastore

datastore_client = datastore.Client()


orders = [
    
    {

    }, 

    {

    }
    
    ]

def add_order_samples(orders):
    kind = "orders"

    for order in orders:
        name = order['id']
        task_key = datastore_client.key(kind, name)
        c_order = datastore.Entity(key=task_key)
        for k, v in order.items():
            c_order[k] = v
        datastore_client.put(c_order)


add_order_samples(orders)
