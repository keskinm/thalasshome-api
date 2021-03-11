import aiohttp
import socketio
from google.cloud import datastore


class Namespace(socketio.AsyncNamespace):

    def __init__(self):
        super(Namespace, self).__init__(namespace='/')

        self.client = datastore.Client()

    @staticmethod
    async def on_connect(sid, *_):
        print(sid)

    async def on_category(self, sid, data):
        query = self.client.query(kind="orders")
        query.add_filter("__key__", "=", self.client.key('orders', int(data['item'])))
        all_keys = query.fetch()

        for i in all_keys:
            i['status'] = data['category']
            self.client.put(i)


if __name__ == "__main__":

    aio_app = aiohttp.web.Application()
    sio = socketio.AsyncServer(cors_allowed_origins='*')

    n = Namespace()
    sio.register_namespace(n)
    sio.attach(aio_app)

    aiohttp.web.run_app(aio_app, port=8000)