#!/usr/bin/python
# Import system modules
import os
# Import local modules
from osinterface import OSinterface
from osinterface import Service
from util import network_retrieval_for_cent
from util import run_shell_cmd

class Cent7OS(OSinterface):
    
    def get_init_path(self):
        return "/usr/sbin/init"
    
    def get_service_list(self):
        service_list = []
        (cmd_out, error) = run_shell_cmd(['/usr/bin/systemctl list-units --type=service --no-pager --plain --no-legend'])
        if error:
            raise Exception(error)
        for service in cmd_out.splitlines():
            service_name = service.split()[0]
            service_file_path = os.path.join('/usr/lib/systemd/system/', service_name)
            service_list.append(Service(service_name, service_file_path))
        return service_list
    
    def get_network_info(self):
        return network_retrieval_for_cent()
