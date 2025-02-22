from google.cloud import datastore
import socketio

from dashboard.lib.master import Master


class Namespace(socketio.AsyncNamespace):
    def __init__(self, sio):
        super(Namespace, self).__init__(namespace='/')

        self.client = datastore.Client()
        self.sio = sio

    async def on_connect(self, sid, *_):
        print("\n ----ON CONECT------ \n")

    async def on_disconnect(self, sid, *_):
        print("\n ----ON DISCONECT------ \n")


    async def on_remove_card(self, sid, data):
        print("\n ----ON REMOVE CARDS------ \n")
        pass

    async def on_remove_cards(self, sid, data):
        list_id = data['list_id']
        print("\n ----ON REMOVE CARDS------ \n")

        query = self.client.query(kind="orders")
        query.add_filter("status", "=", list_id)
        orders = query.fetch()

        for order in orders:
            self.client.delete(order.key)

        await self.sio.emit('remove_cards_client', data={'cards': Master().get_cards(), 'list_id': list_id}, to=sid)

    async def on_select_repl(self, sid, data):
        print("\n ----ON SELECT REPL------ \n")
        select_label = data['select_label']
        item_id = data['item_id']

        print("select_label", select_label)

        query = self.client.query(kind="orders")
        query.add_filter("__key__", "=", self.client.key('orders', int(item_id)))
        orders = query.fetch()

        for order in orders:
            order['replace'] = select_label
            self.client.put(order)
