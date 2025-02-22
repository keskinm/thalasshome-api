
class Hooks:
    def __init__(self, elt_limit=20):
        self.elt_limit = elt_limit
        self.gottens = {'orders/create': {}}

    def check_request(self, request):
        topic = request.headers.get('X-Shopify-Topic')
        hook_id = request.headers.get('X-Shopify-Order-Id')

        if hook_id not in self.gottens[topic]:
            self.gottens[topic][hook_id] = 0
            return True
        else:
            self.gottens[topic][hook_id] += 1
            return False

    def flush(self):
        for k, v in self.gottens.items():
            if len(v) == self.elt_limit:
                self.gottens[k].pop(list(v.keys())[0])
