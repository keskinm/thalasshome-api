from google.cloud import datastore
import aiohttp
import socketio

class Namespace(socketio.AsyncNamespace):

    def __init__(self):
        super(Namespace, self).__init__(namespace='/')

        self.client = datastore.Client()
        self.connected = {}

    async def on_connect(self, sid, *_):
        self.connected[sid] = 'all'

    async def on_disconnect(self, sid, *_):
        if sid in self.connected:
            self.connected.pop(sid)

    async def on_category(self, sid, data):
        query = self.client.query(kind="orders")
        query.add_filter("__key__", "=", self.client.key('orders', int(data['item'])))
        all_keys = query.fetch()

        for i in all_keys:
            i['status'] = data['category']

            if i['status'] not in ['ask', 'delivery', 'client', 'stock', 'done', 'canceled']:
                continue

            self.client.put(i)

        await self.broadcast_update(sid)

    async def broadcast_update(self, x_sid=None):
        cards_z = {'all': get_cards()}  # buffer

        for sid, zone in self.connected.items():
            if sid == x_sid:
                continue

            if zone not in cards_z:
                cards_z[zone] = get_cards(zone)

            await sio.emit('update', data=cards_z[zone], to=sid)

    async def on_trigger_update(self, sid, data):
        if data['key'] != 'update':
            return

        print('TRIGGER UPDATE')

        await self.broadcast_update(sid)

    async def on_ask_zone(self, sid, data):
        cards = get_cards(data['zone'])
        self.connected[sid] = data['zone']

        await sio.emit('update', data=cards, to=sid)



def run_ws():
    aio_app = aiohttp.web.Application()
    sio = socketio.AsyncServer(cors_allowed_origins='*')

    n = Namespace()
    sio.register_namespace(n)
    sio.attach(aio_app)

    aiohttp.web.run_app(aio_app, port=8000)
