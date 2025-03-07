ORDER_SAMPLE_1 = {
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

ORDER_SAMPLE_2 = {}
for k, v in ORDER_SAMPLE_1.items():
    if k == "id":
        ORDER_SAMPLE_2[k] = 3662977106105
    elif k == "shipping_address":
        ORDER_SAMPLE_2[k] = v.copy()
        ORDER_SAMPLE_2[k]["country"] = "Switzerland"
        ORDER_SAMPLE_2[k]["zip"] = "12500"
    else:
        ORDER_SAMPLE_2[k] = v

MIXED_ORDER = {'total_price': '105.00',
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

ORDER_SAMPLES_2021 = [ORDER_SAMPLE_1, ORDER_SAMPLE_2, MIXED_ORDER]


SAMPLE_2025 = {'id': 5545866952887, 'admin_graphql_api_id': 'gid://shopify/Order/5545866952887', 'app_id': 580111, 'browser_ip': '2a02:8428:f959:3201:c2a7:304f:9722:4ac0', 'buyer_accepts_marketing': False, 'cancel_reason': None, 'cancelled_at': None,
               'cart_token': '', # Hide it (git guardian)
               'checkout_id': 43173841469623,
               'checkout_token': '', # Hide it (git guardian)
               'client_details': {'accept_language': 'fr-FR', 'browser_height': None, 'browser_ip': '2a02:8428:f959:3201:c2a7:304f:9722:4ac0', 'browser_width': None, 'session_hash': None, 'user_agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36'}, 'closed_at': None, 'confirmation_number': 'L0YJCIEYW', 'confirmed': True, 'contact_email': 'sign.pls.up@gmail.com', 'created_at': '2025-02-22T22:03:02+01:00', 'currency': 'EUR', 'current_shipping_price_set': {'shop_money': {'amount': '0.00', 'currency_code': 'EUR'}, 'presentment_money': {'amount': '0.00', 'currency_code': 'EUR'}}, 'current_subtotal_price': '80.00', 'current_subtotal_price_set': {'shop_money': {'amount': '80.00', 'currency_code': 'EUR'}, 'presentment_money': {'amount': '80.00', 'currency_code': 'EUR'}}, 'current_total_additional_fees_set': None, 'current_total_discounts': '0.00', 'current_total_discounts_set': {'shop_money': {'amount': '0.00', 'currency_code': 'EUR'}, 'presentment_money': {'amount': '0.00', 'currency_code': 'EUR'}}, 'current_total_duties_set': None, 'current_total_price': '80.00', 'current_total_price_set': {'shop_money': {'amount': '80.00', 'currency_code': 'EUR'}, 'presentment_money': {'amount': '80.00', 'currency_code': 'EUR'}}, 'current_total_tax': '0.00', 'current_total_tax_set': {'shop_money': {'amount': '0.00', 'currency_code': 'EUR'}, 'presentment_money': {'amount': '0.00', 'currency_code': 'EUR'}}, 'customer_locale': 'fr-FR', 'device_id': None, 'discount_codes': [], 'duties_included': False, 'email': 'sign.pls.up@gmail.com', 'estimated_taxes': False, 'financial_status': 'paid', 'fulfillment_status': None, 'landing_site': '/', 'landing_site_ref': None, 'location_id': None, 'merchant_business_entity_id': 'MTU0MTk2NjMzNzgz', 'merchant_of_record_app_id': None, 'name': '#1096', 'note': None, 'note_attributes': [], 'number': 96, 'order_number': 1096, 'order_status_url': 'https://spa-detente.myshopify.com/54196633783/orders/8369c22ca51de36b741acdb10b49e721/authenticate?key=f04c9094de162ecace750443e52d2118', 'original_total_additional_fees_set': None, 'original_total_duties_set': None, 'payment_gateway_names': ['stripe'], 'phone': None, 'po_number': None, 'presentment_currency': 'EUR', 'processed_at': '2025-02-22T22:02:59+01:00', 'reference': None, 'referring_site': '', 'source_identifier': None, 'source_name': 'web', 'source_url': None, 'subtotal_price': '80.00', 'subtotal_price_set': {'shop_money': {'amount': '80.00', 'currency_code': 'EUR'}, 'presentment_money': {'amount': '80.00', 'currency_code': 'EUR'}}, 'tags': '', 'tax_exempt': False, 'tax_lines': [], 'taxes_included': True, 'test': True,
               'token': '', # Hide it (git guardian)
               'total_cash_rounding_payment_adjustment_set': {'shop_money': {'amount': '0.00', 'currency_code': 'EUR'}, 'presentment_money': {'amount': '0.00', 'currency_code': 'EUR'}}, 'total_cash_rounding_refund_adjustment_set': {'shop_money': {'amount': '0.00', 'currency_code': 'EUR'}, 'presentment_money': {'amount': '0.00', 'currency_code': 'EUR'}}, 'total_discounts': '0.00', 'total_discounts_set': {'shop_money': {'amount': '0.00', 'currency_code': 'EUR'}, 'presentment_money': {'amount': '0.00', 'currency_code': 'EUR'}}, 'total_line_items_price': '80.00', 'total_line_items_price_set': {'shop_money': {'amount': '80.00', 'currency_code': 'EUR'}, 'presentment_money': {'amount': '80.00', 'currency_code': 'EUR'}}, 'total_outstanding': '0.00', 'total_price': '80.00', 'total_price_set': {'shop_money': {'amount': '80.00', 'currency_code': 'EUR'}, 'presentment_money': {'amount': '80.00', 'currency_code': 'EUR'}}, 'total_shipping_price_set': {'shop_money': {'amount': '0.00', 'currency_code': 'EUR'}, 'presentment_money': {'amount': '0.00', 'currency_code': 'EUR'}}, 'total_tax': '0.00', 'total_tax_set': {'shop_money': {'amount': '0.00', 'currency_code': 'EUR'}, 'presentment_money': {'amount': '0.00', 'currency_code': 'EUR'}}, 'total_tip_received': '0.00', 'total_weight': 0, 'updated_at': '2025-02-22T22:03:02+01:00', 'user_id': None, 'billing_address': {'first_name': 'Sasha', 'address1': '3 Rue du 11 Novembre 1918', 'phone': None, 'city': 'Le Chambon Feugerolles', 'zip': '42500', 'province': None, 'country': 'France', 'last_name': 'Keskin', 'address2': None, 'company': None, 'latitude': 45.4298948, 'longitude': 4.3899133, 'name': 'Sasha Keskin', 'country_code': 'FR', 'province_code': None}, 'customer': {'id': 7534835990711, 'email': 'sign.pls.up@gmail.com', 'created_at': '2025-02-20T13:26:12+01:00', 'updated_at': '2025-02-22T22:03:02+01:00', 'first_name': 'Sasha', 'last_name': 'Keskin', 'state': 'disabled', 'note': None, 'verified_email': True, 'multipass_identifier': None, 'tax_exempt': False, 'phone': None, 'currency': 'EUR', 'tax_exemptions': [], 'admin_graphql_api_id': 'gid://shopify/Customer/7534835990711', 'default_address': {'id': 8686296563895, 'customer_id': 7534835990711, 'first_name': 'Sasha', 'last_name': 'Keskin', 'company': None, 'address1': '3 Rue du 11 Novembre 1918', 'address2': None, 'city': 'Le Chambon Feugerolles', 'province': None, 'country': 'France', 'zip': '42500', 'phone': None, 'name': 'Sasha Keskin', 'province_code': None, 'country_code': 'FR', 'country_name': 'France', 'default': True}}, 'discount_applications': [], 'fulfillments': [], 'line_items': [{'id': 14121093628087, 'admin_graphql_api_id': 'gid://shopify/LineItem/14121093628087', 'attributed_staffs': [], 'current_quantity': 1, 'fulfillable_quantity': 1, 'fulfillment_service': 'manual', 'fulfillment_status': None, 'gift_card': False, 'grams': 0, 'name': 'Jacuzzi 4 places 1 nuit', 'price': '80.00', 'price_set': {'shop_money': {'amount': '80.00', 'currency_code': 'EUR'}, 'presentment_money': {'amount': '80.00', 'currency_code': 'EUR'}}, 'product_exists': True, 'product_id': 6280065515703, 'properties': [{'name': 'From', 'value': '2025-03-03'}, {'name': 'To', 'value': '2025-03-05'}], 'quantity': 1, 'requires_shipping': True, 'sales_line_item_group_id': None, 'sku': '0', 'taxable': True, 'title': 'Jacuzzi 4 places 1 nuit', 'total_discount': '0.00', 'total_discount_set': {'shop_money': {'amount': '0.00', 'currency_code': 'EUR'}, 'presentment_money': {'amount': '0.00', 'currency_code': 'EUR'}}, 'variant_id': 39329036861623, 'variant_inventory_management': None, 'variant_title': None, 'vendor': 'Thalasshome', 'tax_lines': [], 'duties': [], 'discount_allocations': []}], 'payment_terms': None, 'refunds': [], 'shipping_address': {'first_name': 'Sasha', 'address1': '3 Rue du 11 Novembre 1918', 'phone': None, 'city': 'Le Chambon Feugerolles', 'zip': '42500', 'province': None, 'country': 'France', 'last_name': 'Keskin', 'address2': None, 'company': None, 'latitude': None, 'longitude': None, 'name': 'Sasha Keskin', 'country_code': 'FR', 'province_code': None}, 'shipping_lines': [{'id': 4739836051639, 'carrier_identifier': None, 'code': 'Standard', 'current_discounted_price_set': {'shop_money': {'amount': '0.00', 'currency_code': 'EUR'}, 'presentment_money': {'amount': '0.00', 'currency_code': 'EUR'}}, 'discounted_price': '0.00', 'discounted_price_set': {'shop_money': {'amount': '0.00', 'currency_code': 'EUR'}, 'presentment_money': {'amount': '0.00', 'currency_code': 'EUR'}}, 'is_removed': False, 'phone': None, 'price': '0.00', 'price_set': {'shop_money': {'amount': '0.00', 'currency_code': 'EUR'}, 'presentment_money': {'amount': '0.00', 'currency_code': 'EUR'}}, 'requested_fulfillment_service_id': None, 'source': 'shopify', 'title': 'Standard', 'tax_lines': [], 'discount_allocations': []}], 'returns': []}



