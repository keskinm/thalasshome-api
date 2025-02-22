
from dashboard.utils.maps.maps import zip_codes_to_locations


def find_zone(command_zip, command_country):
    if command_country not in zip_codes_to_locations:
        return None
    for zone, v in zip_codes_to_locations[command_country].items():
        for z_prefix in v:
            if command_zip.startswith(z_prefix):
                return zone
    return None
