from geopy.geocoders import Nominatim

from dashboard.constants import normalize_jac_string


# ----------------- Order ----------------- #

def extract_order_keys(data):
    order = {}
    interest_keys = ['id', 'email', 'created_at', 'updated_at', 'total_price',
                     'line_items', 'shipping_address', 'phone']

    for k, v in data.items():
        if k in interest_keys:
            order[k] = v

    return order

def get_nominatim_coordinates(address):
    geolocator = Nominatim(user_agent="my_geocoder")
    location = geolocator.geocode(address)
    if location:
        return location.latitude, location.longitude
    else:
        return None


def get_coordinates(item):
    if item["billing_address"]["latitude"]:
        lat = item["billing_address"]["latitude"]
        long = item["billing_address"]["longitude"]
    elif item["shipping_address"]["latitude"]:
        lat = item["shipping_address"]["latitude"]
        long = item["shipping_address"]["longitude"]
    else:
        lat, long = get_nominatim_coordinates(f"{item['shipping_address']['address1']} {item['shipping_address']['zip']} {item['shipping_address']['city']} {item['shipping_address']['country']}")
    return lat, long


def get_ship(_item):
    ship = ""
    amount = 0

    for start_separator, item in enumerate(_item):
        ship += " --+-- " if start_separator else ''
        ship += str(item['quantity']) + " " + item['product'] + " "

        ship += ' '.join([
            'Du', item['from_date'], '  Au', item['to_date']
        ]).replace("\\", "")

        amount += item['price']
        #@todo: minus partial payment
        # amount -= item['partial_paid_part']

    return ship, amount


def get_address(item):
    adr_item = item['shipping_address']
    adr = ' '.join([adr_item['city'] or '',
                    adr_item['zip'] or '',
                    adr_item['address1'] or '',
                    adr_item['address2'] or ''])
    return adr


def get_name(item):
    return item['shipping_address']['first_name'] + " " + item['shipping_address']['last_name']


# ----------------- Line Items ----------------- #

def extract_line_items_keys(data, parent_id):
    line_items = []
    interest_keys = ['id', 'quantity', 'price', 'phone', 'name']

    for item in data:
        line_item = {}
        for k, v in item.items():
            if k == "properties":
                v_from = [vv["value"] for vv in v if vv["name"] == "From"][0]
                v_to = [vv["value"] for vv in v if vv["name"] == "To"][0]
                line_item["from_date"] = v_from
                line_item["to_date"] = v_to
            elif k == "name":
                if 'jac' in v:
                    line_item["product"] = normalize_jac_string(v)
                else:
                    line_item["product"] = v
            elif k in interest_keys:
                line_item[k] = v
        if line_item:
            line_item["order_id"] = parent_id
            line_items.append(line_item)

    return line_items

def normalize_line_items(data):
    for item in data:
        item['quantity'] = int(item['quantity'])
        item['price'] = float(item['price'])
    return data
