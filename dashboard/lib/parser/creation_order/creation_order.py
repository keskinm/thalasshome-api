from dashboard.lib.parser.base_parser import BaseParser


class CreationOrderParser(BaseParser):
    def __init__(self):
        BaseParser.__init__(self)
        self.interest_keys = ['id', 'email', 'created_at', 'updated_at', 'gateway', 'total_price', 'title',
                              'line_items', 'shipping_address']

        self.spec_treatment_keys = []
        self.treatment_methods = {}

    def parse_data(self, data):
        order = {}

        for k, v in data.items():
            if k in self.interest_keys:
                order[k] = v

        return order
