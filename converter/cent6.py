#!/usr/bin/python
# Import local
from osinterface import OSinterface
from osinterface import Service
from util import run_shell_cmd
from util import network_retrieval_for_cent

class Cent6OS(OSinterface):
    
    def get_init_path(self):
        return "/sbin/init"
    
    def get_service_list(self):
        service_list = []
        (cmd_out, error) = run_shell_cmd(['chkconfig'])
        if error:
            raise Exception(error)
        records = cmd_out.splitlines()
        for record in records:
            service_name = record.split()[0]
            service_list.append(Service(service_name, "/etc/init.d/%s" % service_name))
        return service_list
    
    def get_network_info(self):
        return network_retrieval_for_cent()
