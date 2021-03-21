from google.cloud import datastore
import socketio

from dashboard.main import get_cards


class Namespace(socketio.AsyncNamespace):
    def __init__(self, sio):
        super(Namespace, self).__init__(namespace='/')

        self.client = datastore.Client()
        self.connected = {}
        self.sio = sio

    async def on_connect(self, sid, *_):
        print("\n ----ON CONECT------ \n")
        self.connected[sid] = 'all'

    async def on_disconnect(self, sid, *_):
        print("\n ----ON DISCONECT------ \n")
        if sid in self.connected:
            self.connected.pop(sid)

    async def on_category(self, sid, data):
        print("\n ----ON CATEGORY------ \n")
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
        print("\n ----BROADCASTING------ \n")
        cards_z = {'all': get_cards()}  # buffer

        for sid, zone in self.connected.items():
            if sid == x_sid:
                continue

            if zone not in cards_z:
                cards_z[zone] = get_cards(zone)

            await self.sio.emit('update', data=cards_z[zone], to=sid)

    async def on_trigger_update(self, sid, data):
        print("\n ----ON TRIGGER UPDATE------ \n")
        if data['key'] != 'update':
            return

        print('TRIGGER UPDATE')

        await self.broadcast_update(sid)

    async def on_ask_zone(self, sid, data):
        print("\n ----ON ASK ZONES------ \n")
        cards = get_cards(data['zone'])
        self.connected[sid] = data['zone']

        await self.sio.emit('update', data=cards, to=sid)

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

        # self.connected[sid] = data['zone']
        # await self.sio.emit('update', data=cards, to=sid)


from sanic import Sanic
from sanic.response import redirect
from sanic import response




def redirect_to_ssl(request):
    attributes = [attr for attr in dir(request)
                  if not attr.startswith('__')]
    print("ICI", attributes, '\n\n\n')

    # request.headers['Access-Control-Allow-Origin'] = '*'
    print("HEADER", request.headers, '\n\n')
    print("URL", request.url, '\n\n')

    # Should we redirect?
    criteria = [
        request.scheme == 'https',
        request.headers.get('X-Forwarded-Proto', 'http') == 'https'
    ]

    if not any(criteria):
        if request.url.startswith('http://'):
            url = request.url.replace('http://', 'https://', 1)
            status = 302
            r = redirect(url, status=status)
            return r


def set_hsts_header(request, response):
    """Adds HSTS header to each response."""
    # Should we add STS header?
    response.headers.setdefault('Strict-Transport-Security', 'max-age={0}'.format(31536000))
    # response.headers['Access-Control-Allow-Origin'] = '*'
    return response


def set_https_redirections():
    app.request_middleware.append(redirect_to_ssl)
    app.response_middleware.append(set_hsts_header)


# set_https_redirections()


app = Sanic(name='my_web_app')

async def index(request):
    return response.html("<h1>Hello World</h1>")

app.add_route(index, "/hello")

sio = socketio.AsyncServer(cors_allowed_origins='*', async_mode='sanic')
sio.register_namespace(Namespace(sio))
sio.attach(app)

app.config['CORS_SUPPORTS_CREDENTIALS'] = True

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)


entry_command = 'gunicorn -b 0.0.0.0:1337 websocket.ws:app --worker-class sanic.worker.GunicornWorker'
