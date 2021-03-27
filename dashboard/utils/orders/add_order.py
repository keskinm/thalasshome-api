from google.cloud import datastore

datastore_client = datastore.Client()

order = {
    "id": 3662977106103,
    "status": "canceled",
    "email": "mouss42490@gmail.com",
    "created_at": "2021-03-09T18:45:08+01:00",
    "updated_at": "2021-03-09T18:45:09+01:00",
    "note": None,
    "gateway": "Cash on Delivery (COD)",
    "total_price": "80.00",
    "subtotal_price": "80.00",
    "title": "4 places 1 nuit",
    "quantity": 1,

    "line_items": [
        {
            "id": 9632848117943,
            "variant_id": 39329036861623,
            "title": "4 places 1 nuit",
            "quantity": 1,
            "sku": "0",
            "variant_title": "",
            "vendor": "spa-detente",
            "fulfillment_service": "manual",
            "product_id": 6280065515703,
            "requires_shipping": True,
            "taxable": True,
            "gift_card": False,
            "name": "4 places 1 nuit",
            "variant_inventory_management": None,
            "properties": [
                {
                    "name": "From",
                    "value": "03\/19\/2021"
                },
                {
                    "name": "start-time",
                    "value": "07:00"
                },
                {
                    "name": "To",
                    "value": "03\/20\/2021"
                },
                {
                    "name": "finish-time",
                    "value": "07:00"
                }
            ],
            "product_exists": True,
            "fulfillable_quantity": 1,
            "grams": 0,
            "price": "80.00",
            "total_discount": "0.00",
            "fulfillment_status": None,
            "price_set": {
                "shop_money": {
                    "amount": "80.00",
                    "currency_code": "EUR"
                },
                "presentment_money": {
                    "amount": "80.00",
                    "currency_code": "EUR"
                }
            },
            "total_discount_set": {
                "shop_money": {
                    "amount": "0.00",
                    "currency_code": "EUR"
                },
                "presentment_money": {
                    "amount": "0.00",
                    "currency_code": "EUR"
                }
            },
            "discount_allocations": [],
            "duties": [],
            "admin_graphql_api_id": "gid:\/\/shopify\/LineItem\/9632848117943",
            "tax_lines": [],
            "origin_location": {
                "id": 2809464455351,
                "country_code": "FR",
                "province_code": "",
                "name": "Thalass Home",
                "address1": "102 Rue d'Estienne d'Orves",
                "address2": "",
                "city": "Verrières-le-Buisson",
                "zip": "91370"
            }
        }
    ],

    "shipping_address": {
        "first_name": "Mustafa",
        "address1": "3 Rue du Onze Novembre",
        "phone": None,
        "city": "Chambon Feugerolles",
        "zip": "42500",
        "province": None,
        "country": "France",
        "last_name": "Keskin",
        "address2": "",
        "company": None,
        "latitude": 45.3971276,
        "longitude": 4.3294953,
        "name": "Mustafa Keskin",
        "country_code": "FR",
        "province_code": None}
}

order1 = {}
for k, v in order.items():
    if k == "id":
        order1[k] = 3662977106105
    elif k == "shipping_address":
        order1[k] = v.copy()
        order1[k]["country"] = "Switzerland"
        order1[k]["zip"] = "12500"
    else:
        order1[k] = v

mixed_order = {'total_price': '105.00',
               'id': '3704443175095',
               'employee': 'None',
               'created_at': '2021-03-27T14:34:30+01:00',
               'email': 'mouss42490@gmail.com',
               "status": "canceled",
               'line_items': [
                   {'gift_card': False, 'fulfillable_quantity': '1', 'discount_allocations': [], 'product_exists': True,
                    'price_set': {'shop_money': {'currency_code': 'EUR', 'amount': '25.00'},
                                  'presentment_money': {'currency_code': 'EUR', 'amount': '25.00'}}, 'price': '25.00',
                    'variant_inventory_management': 'shopify', 'properties': [], 'fulfillment_service': 'manual',
                    'fulfillment_status': None, 'sku': '', 'duties': [], 'id': '9719090053303',
                    'total_discount': '0.00',
                    'origin_location': {'id': '2809464455351', 'city': 'Verrières-le-Buisson',
                                        'address1': "102 Rue d'Estienne d'Orves", 'zip': '91370', 'address2': '',
                                        'name': 'Thalass Home', 'country_code': 'FR', 'province_code': ''},
                    'requires_shipping': True, 'admin_graphql_api_id': 'gid://shopify/LineItem/9719090053303',
                    'total_discount_set': {'shop_money': {'currency_code': 'EUR', 'amount': '0.00'},
                                           'presentment_money': {'amount': '0.00', 'currency_code': 'EUR'}},
                    'vendor': 'Espace Détente', 'product_id': '6280863678647', 'grams': '0', 'tax_lines': [],
                    'name': 'Pack Love',
                    'quantity': '1', 'variant_id': '38162774360247', 'title': 'Pack Love', 'taxable': True,
                    'variant_title': ''},
                   {'fulfillment_service': 'manual', 'discount_allocations': [], 'vendor': 'spa-detente',
                    'name': '4 places 1 nuit', 'price': '80.00', 'taxable': True, 'variant_id': '39329036861623',
                    'id': '9719090086071',
                    'origin_location': {'country_code': 'FR', 'id': '2809464455351',
                                        'address1': "102 Rue d'Estienne d'Orves",
                                        'name': 'Thalass Home', 'address2': '', 'city': 'Verrières-le-Buisson',
                                        'zip': '91370',
                                        'province_code': ''}, 'title': '4 places 1 nuit', 'quantity': '1',
                    'admin_graphql_api_id': 'gid://shopify/LineItem/9719090086071', 'duties': [], 'sku': '0',
                    'gift_card': False,
                    'price_set': {'presentment_money': {'amount': '80.00', 'currency_code': 'EUR'},
                                  'shop_money': {'currency_code': 'EUR', 'amount': '80.00'}},
                    'properties': [{'value': '03/27/2021', 'name': 'From'}, {'name': 'start-time', 'value': '17:00'},
                                   {'value': '03/28/2021', 'name': 'To'}, {'name': 'finish-time', 'value': '07:00'}],
                    'fulfillment_status': None, 'product_exists': True, 'product_id': '6280065515703',
                    'total_discount_set': {'shop_money': {'amount': '0.00', 'currency_code': 'EUR'},
                                           'presentment_money': {'amount': '0.00', 'currency_code': 'EUR'}},
                    'fulfillable_quantity': '1', 'tax_lines': [], 'grams': '0', 'total_discount': '0.00',
                    'requires_shipping': True, 'variant_title': '', 'variant_inventory_management': None}],
               'shipping_address': {'company': None, 'first_name': 'Mustafa', 'phone': None, 'latitude': 45.3971276,
                                    'province_code': None, 'last_name': 'Keskin', 'province': None, 'address2': '',
                                    'zip': '42500', 'country_code': 'FR', 'country': 'France',
                                    'address1': '3 Rue du Onze Novembre', 'longitude': 4.3294953,
                                    'city': 'Chambon Feugerolles',
                                    'name': 'Mustafa Keskin'}, 'gateway': 'Cash on Delivery (COD)',
               'updated_at': '2021-03-27T14:34:31+01:00'}


orders = [order, order1, mixed_order]


def add_order_samples(orders):
    kind = "orders"

    for order in orders:
        name = order['id']
        key = datastore_client.key(kind, name)
        c_order = datastore.Entity(key=key)
        for k, v in order.items():
            c_order[k] = v
        datastore_client.put(c_order)


add_order_samples(orders)
