from dashboard.lib.parser.creation_order import OrderHandler
from google.cloud import datastore
datastore_client = datastore.Client()


class CreationOrderHandler(OrderHandler):
    def __init__(self):
        OrderHandler.__init__(self)

    def insert_received_webhook_to_datastore(self, order):
        name = order['id']
        key = datastore_client.key("orders", name)
        entity = datastore.Entity(key=key)
        
        # @todo how to avoid this stupid thing
        for k, v in order.items():
            entity[k] = v

        datastore_client.put(entity)
