#!/usr/bin/python
# Import 3rd party
from docker import Client
import ast

def get_port_list(remote_docker_endpoint, image_name):
    
    ports = []
    client = Client(base_url=remote_docker_endpoint)
    image = client.inspect_image(image_name)
    labels = image['Config']['Labels']
    if 'network' in labels:
        network_endpoints = ast.literal_eval(labels['network'])
        for endpoint in network_endpoints:
            ports.append(int(endpoint['port']))
    return ports
