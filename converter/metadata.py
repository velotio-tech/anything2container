#!/usr/bin/python
# Import local
from osfactory import get_os_object
from util import convert_list_items_to_string

def generate_metadata(config):
    osobject = get_os_object()
    return {'volumes': config['volumes'],
            'services': convert_list_items_to_string(osobject.get_service_list()),
            'initpath': osobject.get_init_path(),
            'network': convert_list_items_to_string(osobject.get_network_info())}