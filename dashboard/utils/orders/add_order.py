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
