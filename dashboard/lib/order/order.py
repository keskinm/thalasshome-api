from geopy.geocoders import Nominatim

from dashboard.constants import normalize_jac_string

# ----------------- Order ----------------- #


def extract_order_keys(data):
    order = {}
    interest_keys = [
        "id",
        "email",
        "created_at",
        "updated_at",
        "total_price",
        "line_items",
        "shipping_address",
        "phone",
    ]

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
    lat = item["shipping_address"]["latitude"]
    long = item["shipping_address"]["longitude"]
    if not lat or lat == "None":
        lat, long = get_nominatim_coordinates(
            f"{item['shipping_address']['address1']} "
            f"{item['shipping_address']['zip']} "
            f"{item['shipping_address']['city']} "
            f"{item['shipping_address']['country']}"
        )
    return lat, long


def get_ship(_item):
    ship = ""
    amount = 0

    for start_separator, item in enumerate(_item):
        ship += " --+-- " if start_separator else ""
        ship += str(item["quantity"]) + " " + item["product"] + " "

        ship += " ".join(
            ["Du", str(item["from_date"]), "  Au", str(item["to_date"])]
        ).replace("\\", "")

        amount += item["price"]

    return ship, amount


def get_address(item):
    adr_item = item["shipping_address"]
    adr = [
        adr_item.get("city", "") or "",
        adr_item.get("zip", "") or "",
        adr_item.get("address1", "") or "",
        adr_item.get("address2", "") or "",
    ]
    adr = " ".join([s for s in adr if s not in ["", None, "None"]])
    return adr


def get_name(item):
    return (
        item["shipping_address"]["first_name"]
        + " "
        + item["shipping_address"]["last_name"]
    )


# ----------------- Line Items ----------------- #


def extract_line_items_keys(data, parent_id):
    line_items = []
    interest_keys = ["id", "quantity", "price", "phone", "name"]

    for item in data:
        line_item = {}
        discount_amount = None

        for k, v in item.items():
            if k == "properties":
                v_from = [vv["value"] for vv in v if vv["name"] == "From"][0]
                v_to = [vv["value"] for vv in v if vv["name"] == "To"][0]
                line_item["from_date"] = v_from
                line_item["to_date"] = v_to
            elif k == "name":
                if "jac" in v.lower():
                    line_item["product"] = normalize_jac_string(v)
                else:
                    line_item["product"] = v
            elif k == "discount_allocations":
                discount_amount = sum(float(discount["amount"]) for discount in v)
            elif k in interest_keys:
                line_item[k] = v
        if line_item:
            if discount_amount is not None:
                # Overrides price
                line_item["price"] = discount_amount

            line_item["order_id"] = parent_id
            line_items.append(line_item)

    return line_items


def normalize_line_items(data):
    for item in data:
        item["quantity"] = int(item["quantity"])
        item["price"] = float(item["price"])
    return data
