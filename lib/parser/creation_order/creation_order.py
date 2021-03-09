from lib.parser.base_parser import BaseParser


class CreationOrderParser(BaseParser):
    def __init__(self):
        self.interest_keys = ['id', 'email', 'created_at', 'updated_at', 'gateway', 'total_price', 'title', 'properties', 'shipping_address']

        self.spec_treatment_keys = []
        self.treatment_methods = {}


    def parse_data(data):
        order = {}

        for k, v in data.items():
            if k not in self.interest_keys: 
                continue
            
            order[k] = v

        return order
