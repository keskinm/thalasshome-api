from google.cloud import datastore

datastore_client = datastore.Client()


order = {
    "id": 3662977106103,
    "email": "mouss42490@gmail.com",
    "created_at": "2021-03-09T18:45:08+01:00",
    "updated_at": "2021-03-09T18:45:09+01:00",
    "note": None,
    "gateway": "Cash on Delivery (COD)",
    "total_price": "80.00",
    "subtotal_price": "80.00",
    "title": "4 places 1 nuit",
    "quantity": 1,
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
    if k != "id":
        order1[k] = v
    else:
        order1[k] = 3662977106104

orders = [order, order1]


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
