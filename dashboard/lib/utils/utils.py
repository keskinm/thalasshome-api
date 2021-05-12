
from dashboard.utils.maps.maps import zip_codes_to_locations, employees_to_location, employees


def find_zone(command_zip, command_country):
    for zone, v in zip_codes_to_locations[command_country].items():
        for z_prefix in v:
            if command_zip.startswith(z_prefix):
                return zone
    return None
