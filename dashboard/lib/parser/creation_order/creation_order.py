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

    @staticmethod
    def get_ship(item):
        ship = ""
        if 'line_items' in item:
            d_items = item['line_items']
            for start_separator, d_i in enumerate(d_items):
                ship += " --+-- " if start_separator else ''
                ship += d_i['name'] + " "
                if d_i['properties']:
                    prop = {p['name']: p['value'] for p in d_i['properties']}
                    if 'From' in prop:
                        ship += ' '.join(
                            ['Du', prop['From'], prop['start-time'], '  Au', prop['To'], prop['finish-time']]). \
                            replace("\\", "")

        else:
            ship += "Aucun"
        return ship

    @staticmethod
    def get_address(item):
        adr_item = item['shipping_address']
        adr = ' '.join([adr_item['city'], adr_item['zip'], adr_item['address1'], adr_item['address2']])
        return adr
