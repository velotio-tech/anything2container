#!/usr/bin/python

class OSinterface(object):
    
    def get_init_path(self):
        raise NotImplementedError
    
    def get_service_list(self):
        raise NotImplementedError
    
    def get_network_info(self):
        raise NotImplementedError
    
    
class Service():
    
    def __init__(self, name, path):
        self.name = name
        self.path = path
        
    def to_string(self):
        return {'name': self.name,
                'path': self.path}
        
class Network():
    
    def __init__(self, protocol, ip, port, service):
        self.protocol = protocol
        self.ip = ip
        self.port = port
        self.service = service
        
    def to_string(self):
        return {'protocol': self.protocol,
                'ip': self.ip,
                'port': self.port,
                'service': self.service}