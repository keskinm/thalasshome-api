from lib.parser.creation_order.creation_order import CreationOrderParser
from lib.handler.base_handler import BaseHandler

class CreationOrderHandler(CreationOrderParser, BaseHandler):
    def __init__(self):
        CreationOrderParser.__init__(self)
        BaseHandler.__init__(self)
        self.collection_name = "orders"

    def insert_received_webhook_to_datastore(self, order):
        name = order['id']
        key = datastore_client.key(self.collection_name, name)
        entity = datastore.Entity(key=key)
        
        # @todo how to avoid this stupid thing
        for k, v in order.items():
            entity[k] = v

        datastore_client.put(entity)
